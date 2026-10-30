"""App Store 评论采集公共入口；主动拉取与接收 Webhook 分开安装。"""

from .models import AppleReview, AppleReviewsConfig, ReviewApp
from .storage import ReviewStore, ReviewTables, build_review_tables

__all__ = [
    "AppleReview", "AppleReviewsConfig", "ReviewApp", "ReviewStore", "ReviewTables",
    "build_review_tables", "install_review_monitor",
]


def __getattr__(name: str):
    """配置和表声明不加载网络客户端，只有安装运行任务才需要 HTTP 依赖。"""
    if name == "install_review_monitor":
        from .runtime import install_review_monitor

        return install_review_monitor
    raise AttributeError(name)
