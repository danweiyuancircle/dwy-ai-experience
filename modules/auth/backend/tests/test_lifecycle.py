"""会话设备、刷新重放和账户删除使用真实数据库验证隔离边界。"""

from uuid import uuid4

import httpx
import pytest
import test_auth
from dwyeapi.exceptions import AuthenticationError, register_exception_handlers
from fastapi import FastAPI
from sqlalchemy import select

from dwy_app_auth import AuthError, AuthService, install_auth_routes

# 跨模块复用真实数据库fixture，避免复制会话环境。
environment = test_auth.environment


async def test_refresh_replay_revokes_successor_family_only(environment):
    service, _, _, _ = environment
    old = await service.login("a", uuid4())
    independent = await service.login("a", uuid4())
    new = await service.refresh(old.refresh_token)
    with pytest.raises(AuthError):
        await service.refresh(old.refresh_token)
    with pytest.raises(AuthenticationError):
        await service.verify(new.access_token)
    with pytest.raises(AuthError):
        await service.refresh(new.refresh_token)
    assert (await service.verify(independent.access_token)).user_id == old.user.id


async def test_device_listing_and_revoke_are_scoped_to_current_owner(environment):
    service, tables, sessions, verifier = environment
    device, other_device = uuid4(), uuid4()
    first = await service.login("a", device)
    same_device = await service.login("a", device)
    another = await service.login("a", other_device)
    stranger = await service.login("b", device)
    foreign_app = AuthService("rightflow", sessions, tables, verifier)
    foreign = await foreign_app.login("a", device)
    principal = await service.verify(first.access_token)
    page = await service.list_devices(principal, limit=1)
    assert len(page.devices) == 1 and page.next_cursor is not None
    second_page = await service.list_devices(principal, limit=1, cursor=page.next_cursor)
    assert {item.device_id for item in page.devices + second_page.devices} == {device, other_device}
    await service.revoke_device(principal, device)
    for token in (first, same_device):
        with pytest.raises(AuthenticationError):
            await service.verify(token.access_token)
        with pytest.raises(AuthError):
            await service.refresh(token.refresh_token)
    assert (await service.verify(another.access_token)).user_id == first.user.id
    assert (await service.verify(stranger.access_token)).user_id == stranger.user.id
    assert (await foreign_app.verify(foreign.access_token)).user_id == foreign.user.id


async def test_account_deletion_revokes_credentials_and_severs_subject(environment):
    service, tables, sessions, _ = environment
    old = await service.login("a", uuid4())
    other_device = await service.login("a", uuid4())
    stranger = await service.login("b", uuid4())
    result = await service.delete_account(await service.verify(old.access_token))
    assert result.status == "completed"
    for tokens in (old, other_device):
        with pytest.raises(AuthenticationError):
            await service.verify(tokens.access_token)
        with pytest.raises(AuthError):
            await service.refresh(tokens.refresh_token)
    async with sessions() as db:
        user = (
            (await db.execute(select(tables.users).where(tables.users.c.id == str(old.user.id))))
            .mappings()
            .one()
        )
    assert user["disabled"] is True
    assert user["email"] is None and user["display_name"] is None
    assert user["google_subject"] != "google-a"
    fresh = await service.login("a", uuid4())
    assert fresh.user.id != old.user.id
    assert (await service.verify(stranger.access_token)).user_id == stranger.user.id


async def test_account_cleanup_runs_transactionally_and_reports_completion(environment):
    service, tables, sessions, _ = environment
    old = await service.login("a", uuid4())
    called = []

    async def cleanup(db, principal):
        """受控清理可访问同一事务，不删除历史账户账本。"""
        row = (
            (await db.execute(select(tables.users).where(tables.users.c.id == str(principal.user_id))))
            .mappings()
            .one()
        )
        assert row["disabled"] is True
        called.append(principal.user_id)

    service.register_account_cleanup("owned-data", cleanup)
    result = await service.delete_account(await service.verify(old.access_token))
    assert result.status == "completed" and called == [old.user.id]


async def test_account_cleanup_failure_rolls_back_without_false_completion(environment):
    service, tables, sessions, _ = environment
    old = await service.login("a", uuid4())

    async def unavailable_cleanup(db, principal):
        """模拟业务存储异常，账户删除不得报告成功。"""
        raise RuntimeError("cleanup unavailable")

    service.register_account_cleanup("business-data", unavailable_cleanup)
    with pytest.raises(RuntimeError, match="cleanup unavailable"):
        await service.delete_account(await service.verify(old.access_token))
    assert (await service.verify(old.access_token)).user_id == old.user.id
    async with sessions() as db:
        row = (
            (await db.execute(select(tables.users).where(tables.users.c.id == str(old.user.id))))
            .mappings()
            .one()
        )
    assert row["google_subject"] == "google-a" and row["deleted_at"] is None


async def test_account_deletion_preserves_other_application(environment):
    service, tables, sessions, verifier = environment
    foreign = AuthService("rightflow", sessions, tables, verifier)
    old = await service.login("a", uuid4())
    other = await foreign.login("a", uuid4())
    await service.delete_account(await service.verify(old.access_token))
    assert (await foreign.verify(other.access_token)).user_id == other.user.id
    assert (await foreign.login("a", uuid4())).user.id == other.user.id


async def test_account_guard_rejects_deleted_account_and_wrong_app(environment):
    service, tables, sessions, verifier = environment
    old = await service.login("a", uuid4())
    other_app = AuthService("rightflow", sessions, tables, verifier)
    async with sessions() as db, db.begin():
        await service.require_active_account(db, str(old.user.id))
        with pytest.raises(AuthError):
            await other_app.require_active_account(db, str(old.user.id))
    await service.delete_account(await service.verify(old.access_token))
    async with sessions() as db, db.begin():
        with pytest.raises(AuthError):
            await service.require_active_account(db, str(old.user.id))


async def test_lifecycle_rejects_stale_or_forged_principal(environment):
    service, _, _, _ = environment
    first = await service.login("a", uuid4())
    other = await service.login("b", uuid4())
    identity = await service.verify(first.access_token)
    foreign = await service.verify(other.access_token)
    forged = foreign.model_copy(update={"session_id": identity.session_id})
    for invalid in (forged, identity.model_copy(update={"app_id": "rightflow"})):
        with pytest.raises(AuthenticationError):
            await service.delete_account(invalid)
        with pytest.raises(AuthenticationError):
            await service.list_devices(invalid)
        with pytest.raises(AuthenticationError):
            await service.revoke_device(invalid, foreign.device_id)
    await service.logout(identity)
    with pytest.raises(AuthenticationError):
        await service.delete_account(identity)


async def test_http_device_bounds_and_account_contract(environment, tmp_path):
    service, _, _, _ = environment
    app = FastAPI()
    register_exception_handlers(app)
    install_auth_routes(app, service)
    login = await service.login("a", uuid4())
    headers = {"Authorization": "Bearer " + login.access_token}
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            assert (await client.get("/api/v1/devices")).status_code == 401
            for query in ("limit=0", "limit=101", "cursor=invalid", "user_id=" + str(uuid4())):
                assert (await client.get("/api/v1/devices?" + query, headers=headers)).status_code == 422
            response = await client.get("/api/v1/devices", headers=headers)
            assert response.status_code == 200
            assert set(response.json()["data"]["devices"][0]) == {
                "device_id",
                "first_seen_at",
                "last_login_at",
                "active_sessions",
                "current",
            }
            assert response.headers["cache-control"] == "no-store"
            unrelated = await service.login("b", uuid4())
            unrelated_identity = await service.verify(unrelated.access_token)
            assert (
                await client.delete("/api/v1/devices/" + str(unrelated_identity.device_id), headers=headers)
            ).status_code == 404
            second = await service.login("a", uuid4())
            second_identity = await service.verify(second.access_token)
            assert (
                await client.delete("/api/v1/devices/" + str(second_identity.device_id), headers=headers)
            ).status_code == 200
            with pytest.raises(AuthenticationError):
                await service.verify(second.access_token)
            deleted = await client.delete("/api/v1/account", headers=headers)
            assert deleted.status_code == 200 and deleted.json()["data"]["status"] == "completed"
            assert (await client.get("/api/v1/devices", headers=headers)).status_code == 401
