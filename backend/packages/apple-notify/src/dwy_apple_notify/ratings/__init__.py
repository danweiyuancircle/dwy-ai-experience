"""独立的 Apple 全版本评分采集、日周月对比与持久日报。"""

from .client import AppleRatingClient
from .models import AppleRating, AppleRatingsConfig, RatingApp, RatingCollectionError
from .runtime import RatingRuntime, install_rating_monitor
from .service import RatingMonitor
from .storage import RatingStore, RatingTables, build_rating_tables

__all__ = [
    "AppleRating",
    "AppleRatingClient",
    "AppleRatingsConfig",
    "RatingApp",
    "RatingCollectionError",
    "RatingMonitor",
    "RatingRuntime",
    "RatingStore",
    "RatingTables",
    "build_rating_tables",
    "install_rating_monitor",
]
