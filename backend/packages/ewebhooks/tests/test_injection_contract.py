"""显式注入契约：基础库不能自行读取环境配置或创建项目数据库。"""

import base64
import inspect

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from dwy_webhooks.config import WebhookConfig
from dwy_webhooks.fastapi import create_app, install_webhooks


def test_configuration_ignores_environment_and_dotenv(monkeypatch, tmp_path):
    """配置只能由项目构造，环境中的同名字段不得改变显式值或默认值。"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("WEBHOOKS_DISCORD_WEBHOOK_URL=https://evil.example/secret\n")
    monkeypatch.setenv("WEBHOOKS_DISCORD_WEBHOOK_URL", "https://evil.example/secret")
    monkeypatch.setenv("WEBHOOKS_RESEND", '{"secret":"not-injected"}')
    config = WebhookConfig()
    assert config.discord_webhook_url is None and config.resend is None


def test_application_factory_requires_configuration():
    """应用工厂也不能用隐藏的 WebhookConfig() 回读环境。"""
    assert inspect.signature(create_app).parameters["config"].default is inspect.Parameter.empty
    with pytest.raises(TypeError):
        create_app()
    assert isinstance(create_app(WebhookConfig()), FastAPI)


def test_invalid_configuration_does_not_modify_application():
    """错误配置应在注册入口前拒绝，不能留下半套端点。"""
    app = FastAPI()
    count = len(app.routes)
    with pytest.raises(ValidationError):
        config = WebhookConfig(discord_webhook_url="https://evil.example/token")
        install_webhooks(app, config)
    assert len(app.routes) == count


def test_standalone_factory_uses_eapi_error_responses():
    """库创建应用时复用 EAPI 错误边界，项目自己已有的处理器不由安装器覆盖。"""
    config = WebhookConfig(
        discord_webhook_url="https://discord.com/api/webhooks/123456/test-key",
        resend={"secret": "whsec_" + base64.b64encode(b"isolated-signature-key-32bytes").decode()},
    )
    with TestClient(create_app(config)) as client:
        response = client.post("/webhooks/resend", content="{}")
    assert response.status_code == 401
    assert {"code", "message", "data", "timestamp"} <= response.json().keys()


def test_two_sources_cannot_shadow_the_same_route():
    """可配置路径发生冲突应在注册前失败，不能让第一个来源遮蔽第二个。"""
    with pytest.raises(ValidationError):
        WebhookConfig(
            app_store_connect={"apps": {"123": {"name": "App", "secret": "x" * 32}},
                               "path": "/callbacks/{app_id}"},
            apple_notifications={"apps": {"app": {"name": "App", "bundle_id": "com.example.app",
                                  "environment": "Sandbox", "root_certificates": (b"root",)}},
                                 "path": "/callbacks/{app_id}"},
        )


@pytest.mark.parametrize("static,scoped", [
    ("/webhooks/apple/demo", "/webhooks/apple/{app_id}"),
    ("/callbacks/123", "/callbacks/{app_id}"),
])
def test_static_and_parameterized_paths_cannot_overlap(static, scoped):
    """静态来源路由也不能先捕获另一个提供方的 App 通知。"""
    with pytest.raises(ValidationError):
        WebhookConfig(
            resend={"secret": "whsec_" + base64.b64encode(b"scope-regression-secret-32bytes").decode(),
                    "path": static},
            apple_notifications={"apps": {"demo": {"bundle_id": "com.example.demo", "environment": "Sandbox",
                                  "root_certificates": (b"root",)}}, "path": scoped},
        )
