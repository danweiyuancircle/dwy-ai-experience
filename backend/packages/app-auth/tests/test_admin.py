"""独立管理员 HTTP、Cookie 与用户令牌隔离。"""

import httpx
import pytest
from fastapi import FastAPI


async def test_admin_cookie_contract_and_user_token_isolation():
    from dwy_app_auth.admin import AdminAuthConfig, install_admin_auth

    app = FastAPI()
    binding = install_admin_auth(
        app,
        AdminAuthConfig(
            username="operator",
            password="test-only-password",
            secure_cookie=True,
            origin="https://admin.example.com",
        ),
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://admin.example.com"
    ) as client:
        assert (
            await client.get(
                "/api/admin/auth/me",
                headers={
                    "Authorization": "Bearer ac_" + "a" * 43,
                },
            )
        ).status_code == 401
        assert (
            await client.post(
                "/api/admin/auth/login",
                headers={"origin": "https://evil.test"},
                json={"username": "operator", "password": "test-only-password"},
            )
        ).status_code == 403
        response = await client.post(
            "/api/admin/auth/login",
            json={
                "username": "operator",
                "password": "test-only-password",
            },
        )
        assert response.status_code == 200
        assert response.json()["data"] == {"username": "operator"}
        cookie = response.headers["set-cookie"]
        assert all(flag in cookie for flag in ("HttpOnly", "Secure", "SameSite=strict", "Path=/api/admin"))
        token = client.cookies["app_cloud_admin"]
        assert token not in repr(binding.auth.sessions)
        assert (await client.get("/api/admin/auth/me")).status_code == 200
        assert (await client.post("/api/admin/auth/logout")).status_code == 200
        assert binding.auth.resolve(token) is None
        assert (await client.get("/api/admin/auth/me")).status_code == 401


async def test_admin_rejects_oversized_or_secret_inputs_and_limits_attempts():
    from dwy_app_auth.admin import AdminAuthConfig, install_admin_auth

    app = FastAPI()
    install_admin_auth(app, AdminAuthConfig(username="operator", password="test-only-password"))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/admin/auth/login",
            json={
                "username": "operator",
                "password": "secret-private-input",
                "unexpected": True,
            },
        )
        assert response.status_code == 422 and "secret-private-input" not in response.text
        assert response.headers["cache-control"] == "no-store"
        assert (await client.post("/api/admin/auth/login", content="x" * 4097)).status_code == 413
        for _ in range(5):
            assert (
                await client.post(
                    "/api/admin/auth/login",
                    json={
                        "username": "operator",
                        "password": "wrong-password",
                    },
                )
            ).status_code == 401
        limited = await client.post(
            "/api/admin/auth/login",
            json={
                "username": "operator",
                "password": "test-only-password",
            },
        )
        assert limited.status_code == 429 and limited.headers["Retry-After"] == "300"


@pytest.mark.parametrize(
    "origin", ["https://admin.test/", "https://a.test?x=1", "https://u:p@a.test", "https://[", "ftp://a.test"]
)
def test_admin_config_requires_a_valid_explicit_origin(origin):
    from dwy_app_auth.admin import AdminAuthConfig

    with pytest.raises(ValueError):
        AdminAuthConfig(username="operator", password="test-only-password", origin=origin)
