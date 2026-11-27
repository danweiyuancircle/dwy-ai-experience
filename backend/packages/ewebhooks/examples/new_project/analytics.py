"""独立项目接入示例：会话、配置和实际迁移全部由项目拥有。"""

from fastapi import FastAPI
from sqlalchemy import MetaData

from dwy_webhooks.analytics import AppleAnalyticsConfig, build_analytics_tables, install_analytics_monitor


def create_app(config: AppleAnalyticsConfig, sessions) -> FastAPI:
    """注入同一项目的会话；使用暴露的 metadata 做 Alembic 迁移后再启动。

    Args:
        config: 明确配置的账号、App 与通知目标；默认 Asia/Shanghai 08:30。
        sessions: 调用项目通过 eapi 工厂创建的 async_sessionmaker。
    """
    metadata = MetaData()
    tables = build_analytics_tables(metadata)
    app = FastAPI()
    app.state.analytics_metadata = metadata
    install_analytics_monitor(app, config, sessions, tables)
    return app
