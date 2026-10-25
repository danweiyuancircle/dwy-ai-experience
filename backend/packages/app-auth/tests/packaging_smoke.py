"""从新 wheel 环境执行，应用、宿主与 cloud-kernel 必须不存在。"""

import asyncio
import importlib.metadata
import importlib.util
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import dwyeapi
import httpx
from dwyeapi.exceptions import register_exception_handlers
from dwyeapi.identity import Principal
from dwyeapi.providers.email.base import EmailProviderBase
from fastapi import FastAPI
from sqlalchemy import MetaData, inspect, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import dwy_app_auth
from dwy_app_auth import (
    AuthService,
    EapiEmailCodeSender,
    EmailAuthConfig,
    GoogleIdentity,
    SessionPolicy,
    build_auth_tables,
    install_auth_routes,
)
from dwy_app_auth.admin import AdminAuthConfig, install_admin_auth


async def main():
    assert importlib.metadata.version("dwy-app-auth") == "0.1.0"
    assert importlib.metadata.version("dwyeapi") == "0.11.1"
    # 同版本源码不能冒充wheel：两个包必须实际来自新环境的site-packages。
    for module in (dwy_app_auth, dwyeapi):
        assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert callable(getattr(EmailProviderBase, "send_verification_code", None))
    for name in (
        "app_cloud",
        "cloud_kernel",
        "cloud_auth",
        "adbox_server",
        "quadrant_server",
        "rightflow_server",
    ):
        assert importlib.util.find_spec(name) is None, name

    class VerifiedGoogle:
        async def verify(self, token):
            return GoogleIdentity(subject="smoke-subject")

    class MailboxProvider(EmailProviderBase):
        def __init__(self):
            super().__init__(require_common_domain=False)
            self.messages = []
            self.languages = []

        async def _send(self, target, code, *, language="en"):
            self.messages.append((target, code))
            self.languages.append(language)
            return True

        async def _get_redis(self):
            raise AssertionError("Email authentication must not use Redis")

    with TemporaryDirectory() as directory:
        engine = create_async_engine(f"sqlite+aiosqlite:///{directory}/auth.db")
        metadata = MetaData()
        tables = build_auth_tables(metadata)
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
            # 固定外部契约，不从本轮metadata反推验收期待值。
            actual_tables = await connection.run_sync(lambda bind: set(inspect(bind).get_table_names()))
            assert actual_tables == {
                "auth_users",
                "auth_sessions",
                "auth_refresh_history",
                "auth_password_credentials",
                "auth_email_challenges",
                "auth_rate_limits",
            }
        sessions = async_sessionmaker(engine)
        mailbox = MailboxProvider()
        service = AuthService(
            "smoke",
            sessions,
            tables,
            VerifiedGoogle(),
            email_sender=EapiEmailCodeSender(mailbox),
            email_config=EmailAuthConfig(challenge_secret="isolated-smoke-only-secret-value-2026"),
            session_policy=SessionPolicy(refresh_ttl=180 * 86400, rolling_refresh=True),
        )
        app = FastAPI()
        register_exception_handlers(app)
        install_auth_routes(app, service)
        install_admin_auth(app, AdminAuthConfig(username="smoke", password="smoke-test-password"))
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
        ):
            password = "isolated wheel password"
            code_response = await client.post(
                "/api/v1/auth/email/code", json={"email": "wheel@example.com", "purpose": "register"}
            )
            assert code_response.status_code == 200
            assert mailbox.languages == ["en"]
            chinese_code = await client.post(
                "/api/v1/auth/email/code",
                headers={"Accept-Language": "zh-Hant-TW"},
                json={"email": "chinese@example.com", "purpose": "register"},
            )
            assert chinese_code.status_code == 200
            assert mailbox.languages == ["en", "zh"]
            assert 'lang="en"' in mailbox._render_code_html("123456")
            assert 'lang="zh-CN"' in mailbox._render_code_html("123456", language="zh")
            challenge = code_response.json()["data"]
            assert set(challenge) == {"challenge_id", "expires_in", "resend_after", "code_length"}
            assert challenge["code_length"] == 6
            registered = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "wheel@example.com",
                    "password": password,
                    "device_id": str(uuid4()),
                    "code": mailbox.messages[0][1],
                    "challenge_id": challenge["challenge_id"],
                },
            )
            assert registered.status_code == 200 and registered.json()["code"] == "SUCCESS"
            registered_tokens = registered.json()["data"]
            email_identity = await service.verify(registered_tokens["access_token"])
            email_login = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "WHEEL@example.com",
                    "password": password,
                    "device_id": str(uuid4()),
                },
            )
            assert email_login.status_code == 200
            email_tokens = email_login.json()["data"]
            assert email_tokens["user"]["id"] == registered_tokens["user"]["id"]
            async with sessions() as db:
                deadline = await db.scalar(
                    select(tables.sessions.c.refresh_expires_at).where(
                        tables.sessions.c.id == str(email_identity.session_id)
                    )
                )
                assert abs(deadline - int(time.time()) - 180 * 86400) <= 2
                credential = (await db.execute(select(tables.password_credentials))).mappings().one()
                assert credential["password_hash"].startswith("$2") and password not in str(credential)
            rotated = await client.post(
                "/api/v1/auth/refresh", json={"refresh_token": email_tokens["refresh_token"]}
            )
            assert rotated.status_code == 200
            email_tokens = rotated.json()["data"]
            reset_code = await client.post(
                "/api/v1/auth/email/code", json={"email": "wheel@example.com", "purpose": "password_reset"}
            )
            assert reset_code.status_code == 200
            reset = await client.post(
                "/api/v1/auth/password/reset",
                json={
                    "email": "wheel@example.com",
                    "password": "new isolated wheel password",
                    "code": mailbox.messages[-1][1],
                    "challenge_id": reset_code.json()["data"]["challenge_id"],
                },
            )
            assert reset.status_code == 200 and reset.json()["data"] == {"status": "completed"}
            for old in (registered_tokens, email_tokens):
                assert (
                    await client.get(
                        "/api/v1/devices", headers={"Authorization": "Bearer " + old["access_token"]}
                    )
                ).status_code == 401
                assert (
                    await client.post("/api/v1/auth/refresh", json={"refresh_token": old["refresh_token"]})
                ).status_code == 401
            assert (
                await client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": "wheel@example.com",
                        "password": "new isolated wheel password",
                        "device_id": str(uuid4()),
                    },
                )
            ).status_code == 200
            login = await client.post(
                "/api/v1/auth/google", json={"id_token": "verified", "device_id": str(uuid4())}
            )
            assert login.status_code == 200
            tokens = login.json()["data"]
            assert isinstance(await service.verify(tokens["access_token"]), Principal)
            headers = {"Authorization": "Bearer " + tokens["access_token"]}
            assert (await client.get("/api/admin/auth/me", headers=headers)).status_code == 401
            admin = await client.post(
                "/api/admin/auth/login",
                json={
                    "username": "smoke",
                    "password": "smoke-test-password",
                },
            )
            assert admin.status_code == 200
            assert (await client.get("/api/v1/devices")).status_code == 401
            assert (await client.get("/api/v1/devices", headers=headers)).status_code == 200
            assert (await client.delete("/api/v1/account", headers=headers)).status_code == 200
            assert (await client.get("/api/v1/devices", headers=headers)).status_code == 401
        await engine.dispose()
    print(
        "dwy-app-auth wheel: isolated imports, EAPI identity, Google sessions, "
        "fixed six-table contract, email transport/register/login/reset revocation, rolling policy, "
        "admin Cookie isolation, deletion verified"
    )


if __name__ == "__main__":
    asyncio.run(main())
