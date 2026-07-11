"""全局时间工具 — 所有日期 / 时长操作的唯一入口。

业务时间统一 Asia/Shanghai, JWT 等协议场景提供 UTC 方法。
禁止在业务代码中直接使用 ``datetime.now()`` / ``datetime.utcnow()`` /
``from datetime import timedelta``,统一通过本模块访问。

Usage::

    from dwyeapi import dt

    dt.now()                      # naive datetime, 中国时间, 用于数据库
    dt.now_str()                  # "2026-04-06 14:30:00"
    dt.today()                    # date(2026, 4, 6)
    dt.timestamp()                # Unix 时间戳(秒)
    dt.utc_now()                  # aware datetime, UTC, 用于 JWT

    dt.timedelta(minutes=10)      # 时长(透传 stdlib timedelta)
    dt.after(days=1)              # now + 偏移(naive 中国时间)
    dt.before(hours=1)            # now - 偏移
    dt.utc_after(minutes=30)      # utc_now + 偏移(aware UTC, JWT exp)
    dt.utc_before(days=1)         # utc_now - 偏移
"""

from datetime import date, datetime
from datetime import timedelta as _Timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")

# 公开 re-export:业务侧用 dt.timedelta(...),不再 from datetime import timedelta
timedelta = _Timedelta


# ── 业务时间(Asia/Shanghai) ──────────────────────────────────────────


def now() -> datetime:
    """当前中国时间(naive, 用于数据库存储)。"""
    return datetime.now(TZ).replace(tzinfo=None)


def now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化的当前中国时间字符串。"""
    return datetime.now(TZ).strftime(fmt)


def today() -> date:
    """当前中国日期。"""
    return datetime.now(TZ).date()


def timestamp() -> float:
    """当前 Unix 时间戳(秒)。"""
    return datetime.now(TZ).timestamp()


def after(**kwargs: int | float) -> datetime:
    """当前中国时间加上偏移,返回 naive datetime(写库 / 业务截止时间)。

    Args:
        **kwargs: 同 ``datetime.timedelta`` 关键字参数
            (``days`` / ``seconds`` / ``microseconds`` / ``milliseconds`` /
            ``minutes`` / ``hours`` / ``weeks``)。示例:``days=1, hours=2``。

    Returns:
        datetime: ``now() + timedelta(**kwargs)``,无时区信息。
    """
    return now() + _Timedelta(**kwargs)


def before(**kwargs: int | float) -> datetime:
    """当前中国时间减去偏移,返回 naive datetime。

    Args:
        **kwargs: 同 ``after``。示例:``hours=1``。

    Returns:
        datetime: ``now() - timedelta(**kwargs)``,无时区信息。
    """
    return now() - _Timedelta(**kwargs)


# ── UTC(JWT 等协议场景) ──────────────────────────────────────────────


def utc_now() -> datetime:
    """当前 UTC 时间(aware, 用于 JWT exp 等协议字段)。"""
    return datetime.now(UTC)


def utc_after(**kwargs: int | float) -> datetime:
    """当前 UTC 时间加上偏移,返回 aware datetime(JWT exp 等)。

    Args:
        **kwargs: 同 ``after``。示例:``minutes=30``。

    Returns:
        datetime: ``utc_now() + timedelta(**kwargs)``,tzinfo=UTC。
    """
    return utc_now() + _Timedelta(**kwargs)


def utc_before(**kwargs: int | float) -> datetime:
    """当前 UTC 时间减去偏移,返回 aware datetime。

    Args:
        **kwargs: 同 ``after``。示例:``days=1``。

    Returns:
        datetime: ``utc_now() - timedelta(**kwargs)``,tzinfo=UTC。
    """
    return utc_now() - _Timedelta(**kwargs)
