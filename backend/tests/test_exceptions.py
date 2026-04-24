"""Tests for dwyeapi.exceptions."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from dwyeapi.config import set_current_environment
from dwyeapi.exceptions import (
    AppError,
    AuthenticationError,
    BusinessError,
    NotFoundError,
    PermissionDeniedError,
    register_exception_handlers,
)


class TestAppErrorHierarchy:
    def test_app_error_defaults(self):
        err = AppError(message="something broke")
        assert err.message == "something broke"
        assert err.code == "UNKNOWN_ERROR"

    def test_app_error_custom_code(self):
        err = AppError(message="oops", code="CUSTOM")
        assert err.code == "CUSTOM"

    def test_not_found_error(self):
        err = NotFoundError("用户")
        assert err.message == "用户不存在"
        assert err.code == "NOT_FOUND"
        assert isinstance(err, AppError)

    def test_business_error(self):
        err = BusinessError(message="余额不足", code="INSUFFICIENT_BALANCE")
        assert err.message == "余额不足"
        assert isinstance(err, AppError)

    def test_permission_denied_error(self):
        err = PermissionDeniedError()
        assert err.message == "权限不足"
        assert err.code == "PERMISSION_DENIED"

    def test_authentication_error(self):
        err = AuthenticationError()
        assert err.message == "认证失败"
        assert err.code == "AUTHENTICATION_FAILED"


class _Item(BaseModel):
    """仅用于触发 RequestValidationError 的测试 schema。"""

    name: str
    qty: int


class TestExceptionHandlers:
    @pytest.fixture()
    def app(self):
        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/not-found")
        async def raise_not_found():
            raise NotFoundError("订单")

        @app.get("/business-error")
        async def raise_business():
            raise BusinessError(message="余额不足", code="INSUFFICIENT_BALANCE")

        @app.get("/forbidden")
        async def raise_forbidden():
            raise PermissionDeniedError()

        @app.get("/unauthorized")
        async def raise_auth():
            raise AuthenticationError()

        @app.post("/validate")
        async def validate_body(item: _Item):
            return {"ok": True, "item": item.model_dump()}

        @app.get("/teapot")
        async def raise_teapot():
            raise HTTPException(status_code=418, detail="I'm a teapot", headers={"X-Test": "yes"})

        @app.get("/oauth2-challenge")
        async def raise_oauth2():
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        @app.get("/boom")
        async def raise_unhandled():
            raise KeyError("secret_field")

        return app

    @pytest.fixture()
    def client(self, app):
        return TestClient(app, raise_server_exceptions=False)

    def test_not_found_returns_404(self, client):
        resp = client.get("/not-found")
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == "NOT_FOUND"
        assert body["message"] == "订单不存在"
        assert body["data"] is None
        assert isinstance(body["timestamp"], int)

    def test_business_error_returns_422(self, client):
        resp = client.get("/business-error")
        assert resp.status_code == 422
        body = resp.json()
        assert body["code"] == "INSUFFICIENT_BALANCE"
        assert body["message"] == "余额不足"
        assert body["data"] is None
        assert isinstance(body["timestamp"], int)

    def test_permission_denied_returns_403(self, client):
        resp = client.get("/forbidden")
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "PERMISSION_DENIED"
        assert body["data"] is None

    def test_authentication_error_returns_401(self, client):
        resp = client.get("/unauthorized")
        assert resp.status_code == 401
        body = resp.json()
        assert body["code"] == "AUTHENTICATION_FAILED"
        assert body["data"] is None

    def test_request_validation_error_returns_422(self, client):
        resp = client.post("/validate", json={"qty": "not-an-int"})
        assert resp.status_code == 422
        body = resp.json()
        assert body["code"] == "VALIDATION_ERROR"
        assert body["message"] == "请求参数校验失败"
        assert isinstance(body["timestamp"], int)
        errors = body["data"]["errors"]
        assert isinstance(errors, list)
        assert len(errors) >= 1
        for item in errors:
            assert "field" in item
            assert "message" in item
            assert isinstance(item["field"], str)
            assert isinstance(item["message"], str)

    def test_http_exception_returns_status_and_envelope(self, client):
        resp = client.get("/teapot")
        assert resp.status_code == 418
        body = resp.json()
        assert body["code"] == "HTTP_418"
        assert body["message"] == "I'm a teapot"
        assert body["data"] is None
        # headers 透传校验
        assert resp.headers.get("X-Test") == "yes"

    def test_http_exception_oauth2_www_authenticate_preserved(self, client):
        resp = client.get("/oauth2-challenge")
        assert resp.status_code == 401
        assert resp.headers.get("WWW-Authenticate") == "Bearer"

    def test_unhandled_exception_dev_mode_includes_detail(self, client):
        try:
            set_current_environment("dev")
            resp = client.get("/boom")
        finally:
            set_current_environment("prod")
        assert resp.status_code == 500
        body = resp.json()
        assert body["code"] == "INTERNAL_ERROR"
        assert "secret_field" in body["message"]
        assert body["data"] is None

    def test_unhandled_exception_prod_mode_masks_detail(self, client):
        # 显式保证 prod(测试默认 fixture 也是 prod,但这里明示意图)
        set_current_environment("prod")
        resp = client.get("/boom")
        assert resp.status_code == 500
        body = resp.json()
        assert body["code"] == "INTERNAL_ERROR"
        assert body["message"] == "服务器内部错误"
        assert "secret_field" not in body["message"]
        assert body["data"] is None
