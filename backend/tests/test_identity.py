"""应用身份合同与显式 Bearer 验证边界。"""

from typing import Annotated
from uuid import uuid4

import httpx
import pytest
from fastapi import Depends, FastAPI
from pydantic import ValidationError

from dwyeapi.exceptions import register_exception_handlers


def test_principal_is_strict_and_immutable():
    from dwyeapi.identity import Principal

    identity = Principal(app_id="adbox", user_id=uuid4(), session_id=uuid4(), device_id=uuid4())
    with pytest.raises(ValidationError):
        Principal(**{**identity.model_dump(), "user_id": str(identity.user_id)})
    with pytest.raises(ValidationError):
        identity.app_id = "rightflow"


async def test_identity_dependency_rejects_wrong_app_and_malformed_credentials():
    from dwyeapi.identity import Principal, create_identity_dependency

    class Verifier:
        async def verify(self, token):
            return Principal(app_id=token, user_id=uuid4(), session_id=uuid4(), device_id=uuid4())

    app = FastAPI()
    register_exception_handlers(app)
    principal = create_identity_dependency("adbox", Verifier(), authorization_limit=64)

    @app.get("/owned")
    async def owned(identity: Annotated[object, Depends(principal)]):
        return {"app_id": identity.app_id}

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        for value in ("", "Basic adbox", "Bearer ", "Bearer adbox more", "Bearer " + "a" * 65, "Bearer rightflow"):
            assert (await client.get("/owned", headers={"authorization": value})).status_code == 401
        assert (await client.get("/owned", headers={"authorization": "Bearer adbox"})).json() == {"app_id": "adbox"}
