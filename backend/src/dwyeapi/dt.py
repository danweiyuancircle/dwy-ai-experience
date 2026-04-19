"""全局时间工具 — 所有日期操作的唯一入口。

业务时间统一 Asia/Shanghai，JWT 等协议场景提供 UTC 方法。
禁止在业务代码中直接使用 datetime.now()，统一通过本模块访问。

Usage::

    from dwyeapi import dt

    dt.now()          # naive datetime, 中国时间, 用于数据库
    dt.now_str()      # "2026-04-06 14:30:00"
    dt.today()        # date(2026, 4, 6)
    dt.timestamp()    # Unix 时间戳（秒）
    dt.utc_now()      # aware datetime, UTC, 用于 JWT
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")


# ── 业务时间（Asia/Shanghai） ──────────────────────────────────────────


def now() -> datetime:
    """当前中国时间（naive，用于数据库存储）。"""
    return datetime.now(TZ).replace(tzinfo=None)


def now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化的当前中国时间字符串。"""
    return datetime.now(TZ).strftime(fmt)


def today() -> date:
    """当前中国日期。"""
    return datetime.now(TZ).date()


def timestamp() -> float:
    """当前 Unix 时间戳（秒）。"""
    return datetime.now(TZ).timestamp()


# ── UTC（JWT 等协议场景） ──────────────────────────────────────────────


def utc_now() -> datetime:
    """当前 UTC 时间（aware，用于 JWT exp 等协议字段）。"""
    return datetime.now(UTC)
