"""独立项目示例：项目创建配置后注入，不依赖 App Cloud 的任何包。"""

from dwyeapi.exceptions import register_exception_handlers
from fastapi import FastAPI

from dwy_webhooks import WebhookConfig, WebhookSinks, install_webhooks
from dwy_webhooks.sinks import ReceiptStore


def create_project_app(config: WebhookConfig, *, sinks: WebhookSinks | None = None,
                       receipts: ReceiptStore | None = None) -> FastAPI:
    """配置、密钥取得方式和可选资源均由调用项目决定。"""
    app = FastAPI(title="Independent webhook consumer")
    register_exception_handlers(app)

    @app.get("/status")
    def status():
        """项目自己的端点用于确认集成不会占用整个应用。"""
        return {"status": "ok"}

    install_webhooks(app, config, sinks=sinks, receipts=receipts)
    return app
