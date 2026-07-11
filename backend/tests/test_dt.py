"""Tests for dwyeapi.dt — 时钟与时长统一入口。"""

from datetime import datetime, timedelta, timezone

from dwyeapi import dt


class TestClock:
    def test_now_is_naive(self):
        assert dt.now().tzinfo is None

    def test_utc_now_is_aware_utc(self):
        now = dt.utc_now()
        assert now.tzinfo is not None
        # 与 UTC 偏移为 0
        assert now.utcoffset() == timedelta(0)

    def test_today_is_date(self):
        assert dt.today() == dt.now().date()

    def test_timestamp_is_float(self):
        ts = dt.timestamp()
        assert isinstance(ts, float)
        assert ts > 0


class TestTimedelta:
    def test_timedelta_reexport(self):
        delta = dt.timedelta(minutes=10)
        assert isinstance(delta, timedelta)
        assert delta == timedelta(minutes=10)

    def test_timedelta_days_and_hours(self):
        assert dt.timedelta(days=1, hours=2) == timedelta(days=1, hours=2)


class TestAfterBefore:
    def test_after_is_naive_and_future(self):
        base = dt.now()
        future = dt.after(minutes=5)
        assert future.tzinfo is None
        assert future > base
        # 约 5 分钟,允许毫秒级误差
        assert abs((future - base).total_seconds() - 300) < 1

    def test_before_is_naive_and_past(self):
        base = dt.now()
        past = dt.before(hours=1)
        assert past.tzinfo is None
        assert past < base
        assert abs((base - past).total_seconds() - 3600) < 1

    def test_utc_after_is_aware_and_future(self):
        base = dt.utc_now()
        future = dt.utc_after(minutes=30)
        assert future.tzinfo is not None
        assert future.utcoffset() == timedelta(0)
        assert future > base
        assert abs((future - base).total_seconds() - 1800) < 1

    def test_utc_before_is_aware_and_past(self):
        base = dt.utc_now()
        past = dt.utc_before(days=1)
        assert past.tzinfo is not None
        assert past < base
        assert abs((base - past).total_seconds() - 86400) < 1

    def test_utc_after_compatible_with_jwt_exp(self):
        """utc_after 结果可直接写入 JWT exp(aware UTC)。"""
        exp = dt.utc_after(minutes=10)
        # python-jose 接受 datetime;这里只校验形态
        assert isinstance(exp, datetime)
        assert exp.tzinfo is not None
        # 与 timezone.utc 兼容
        assert exp.astimezone(timezone.utc).tzinfo is not None
