"""Tests for danweiyuan_eapi.exceptions."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from danweiyuan_eapi.exceptions import (
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

        return app

    @pytest.fixture()
    def client(self, app):
        return TestClient(app)

    def test_not_found_returns_404(self, client):
        resp = client.get("/not-found")
        assert resp.status_code == 404
        assert resp.json() == {"code": "NOT_FOUND", "message": "订单不存在"}

    def test_business_error_returns_422(self, client):
        resp = client.get("/business-error")
        assert resp.status_code == 422
        assert resp.json() == {"code": "INSUFFICIENT_BALANCE", "message": "余额不足"}

    def test_permission_denied_returns_403(self, client):
        resp = client.get("/forbidden")
        assert resp.status_code == 403

    def test_authentication_error_returns_401(self, client):
        resp = client.get("/unauthorized")
        assert resp.status_code == 401
