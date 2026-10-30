"""Apple 经营快照和日报公共入口；表声明不触发网络或数据库初始化。"""

from .formatting import apple_business_digest_content
from .models import (
    AnalyticsApp,
    AnalyticsCollectionError,
    AnalyticsValue,
    AppleAnalyticsConfig,
    AppleBusinessSnapshot,
)
from .storage import AnalyticsStore, AnalyticsTables, build_analytics_tables

__all__ = [
    "AnalyticsApp",
    "AnalyticsCollectionError",
    "AnalyticsValue",
    "AppleAnalyticsConfig",
    "AppleBusinessSnapshot",
    "AnalyticsStore",
    "AnalyticsTables",
    "build_analytics_tables",
    "apple_business_digest_content",
    "AppleAnalyticsClient",
    "AnalyticsMonitor",
    "AnalyticsRuntime",
    "install_analytics_monitor",
]


def __getattr__(name: str):
    """仅使用配置和迁移定义时不加载 HTTPX；安装任务才加载网络客户端。"""
    if name == "AppleAnalyticsClient":
        from .client import AppleAnalyticsClient

        return AppleAnalyticsClient
    if name == "AnalyticsMonitor":
        from .service import AnalyticsMonitor

        return AnalyticsMonitor
    if name in ("AnalyticsRuntime", "install_analytics_monitor"):
        from .runtime import AnalyticsRuntime, install_analytics_monitor

        return {"AnalyticsRuntime": AnalyticsRuntime, "install_analytics_monitor": install_analytics_monitor}[
            name
        ]
    raise AttributeError(name)
