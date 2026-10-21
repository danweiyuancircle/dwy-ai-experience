"""从新 wheel 环境执行，应用、宿主与 cloud-kernel 必须不存在。"""

import asyncio
import importlib.metadata
import importlib.util
from tempfile import TemporaryDirectory
from uuid import uuid4

import httpx
from dwyeapi.exceptions import register_exception_handlers
from dwyeapi.identity import Principal
from fastapi import FastAPI
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_app_auth import AuthService, GoogleIdentity, build_auth_tables, install_auth_routes
from dwy_app_auth.admin import AdminAuthConfig, install_admin_auth


async def main():
    assert importlib.metadata.version("dwy-app-auth") == "0.1.0"
    assert importlib.metadata.version("dwyeapi") == "0.11.1"
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

    with TemporaryDirectory() as directory:
        engine = create_async_engine(f"sqlite+aiosqlite:///{directory}/auth.db")
        metadata = MetaData()
        tables = build_auth_tables(metadata)
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        service = AuthService("smoke", async_sessionmaker(engine), tables, VerifiedGoogle())
        app = FastAPI()
        register_exception_handlers(app)
        install_auth_routes(app, service)
        install_admin_auth(app, AdminAuthConfig(username="smoke", password="smoke-test-password"))
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
        ):
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
        "admin Cookie isolation, deletion verified"
    )


if __name__ == "__main__":
    asyncio.run(main())
