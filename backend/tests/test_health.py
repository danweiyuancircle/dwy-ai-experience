"""Tests for dwyeapi.health."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dwyeapi.health import create_health_router


def _make_app(**kwargs) -> FastAPI:
    """构造挂载健康路由的 FastAPI app。"""
    app = FastAPI()
    router = create_health_router(
        service_name=kwargs.pop("service_name", "test-service"),
        version=kwargs.pop("version", "9.9.9"),
        **kwargs,
    )
    app.include_router(router)
    return app


class TestHealthRouter:
    def test_default_path_returns_alive(self):
        app = _make_app(service_name="quant-cloud", version="1.0.0")
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == "SUCCESS"
        assert body["message"] == "success"
        assert body["data"] == {
            "service": "quant-cloud",
            "version": "1.0.0",
            "status": "alive",
        }
        assert isinstance(body["timestamp"], int)

    def test_custom_path(self):
        app = _make_app(path="/api/healthz")
        client = TestClient(app)
        assert client.get("/api/healthz").status_code == 200
        assert client.get("/health").status_code == 404

    def test_include_in_schema_false_hides_from_openapi(self):
        app = _make_app(include_in_schema=False)
        client = TestClient(app)
        spec = client.get("/openapi.json").json()
        assert "/health" not in spec.get("paths", {})

    def test_include_in_schema_true_shows_in_openapi(self):
        app = _make_app()
        client = TestClient(app)
        spec = client.get("/openapi.json").json()
        assert "/health" in spec.get("paths", {})

    def test_response_envelope_shape(self):
        app = _make_app(service_name="svc", version="2.3.4")
        client = TestClient(app)
        body = client.get("/health").json()
        assert set(body.keys()) == {"code", "message", "data", "timestamp"}
        assert set(body["data"].keys()) == {"service", "version", "status"}
        assert body["data"]["service"] == "svc"
        assert body["data"]["version"] == "2.3.4"
        assert body["data"]["status"] == "alive"


@pytest.mark.parametrize(
    ("service_name", "version"),
    [("svc-a", "0.0.1"), ("svc-b", "10.20.30")],
)
def test_returns_passed_metadata(service_name: str, version: str):
    """不同 service_name / version 组合都能如实回显。"""
    app = _make_app(service_name=service_name, version=version)
    client = TestClient(app)
    data = client.get("/health").json()["data"]
    assert data["service"] == service_name
    assert data["version"] == version
