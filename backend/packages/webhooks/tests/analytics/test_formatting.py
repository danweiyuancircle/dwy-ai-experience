"""日报和周报不得把缺失、存量或独立设备当作可相加流量。"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from dwy_webhooks.analytics.formatting import apple_business_digest_content
from dwy_webhooks.analytics.models import AnalyticsValue, AppleBusinessSnapshot


def daily(day=date(2026, 10, 25), **metrics):
    return AppleBusinessSnapshot(
        app_id="123",
        report_date=day,
        metrics={
            key: value
            if isinstance(value, AnalyticsValue)
            else AnalyticsValue(
                value=Decimal(str(value)),
                status="available",
                source="Apple",
                currency="USD" if key.endswith("usd") else None,
            )
            for key, value in metrics.items()
        },
    )


def text(snapshots, **kwargs):
    return "\n".join(apple_business_digest_content("工具", snapshots, **kwargs))


def test_daily_explicit_date_currency_status_source_and_safe_comparison():
    rendered = text(
        [
            daily(
                sales_usd="-1.25",
                first_downloads=3,
                renewals=AnalyticsValue(status="pending", source="Subscriptions"),
            )
        ],
        comparison=[daily(date(2026, 10, 24), sales_usd=0, first_downloads=2)],
    )
    assert "2026-10-25" in rendered and "USD -1.25" in rendered
    assert "待发布" in rendered and "不可用" in rendered and "Apple" in rendered
    assert "+50.0%" in rendered and "基期为 0" in rendered
    assert "MRR" not in rendered and "@everyone" not in rendered


def test_weekly_sums_only_complete_flows_and_uses_endpoint_stocks():
    start = date(2026, 10, 19)
    days = [
        daily(
            start + timedelta(days=i),
            first_downloads=2,
            paid_subscriptions=10 + i,
            impressions=5,
            sales_usd=1,
        )
        for i in range(7)
    ]
    previous = [
        daily(start - timedelta(days=7 - i), first_downloads=1, paid_subscriptions=3 + i, sales_usd=1)
        for i in range(7)
    ]
    rendered = text(days, period="weekly", comparison=previous)
    assert "首次下载：14" in rendered and "+100.0%" in rendered
    assert "付费订阅存量：16" in rendered and "期末" in rendered
    assert "曝光：35" not in rendered and "不可累加" in rendered
    partial = days[:-1] + [daily(start + timedelta(days=6), paid_subscriptions=16)]
    assert "首次下载：数据不完整" in text(partial, period="weekly")


def test_comparisons_require_matching_sources_and_contiguous_periods():
    current = daily(first_downloads=2)
    previous = daily(
        date(2026, 10, 24), first_downloads=AnalyticsValue(value=1, status="available", source="Other")
    )
    assert "+100.0%" not in text([current], comparison=[previous])
    with pytest.raises(ValueError):
        apple_business_digest_content("工具", [current], period="weekly")
    with pytest.raises(ValueError):
        apple_business_digest_content("工具", [current, current])


def test_deterministic_utf16_parts_keep_full_lines_and_dimension_coverage():
    snap = daily(first_downloads=2).model_copy(
        update={
            "breakdowns": {"download_territories": {"USA": Decimal(2), "UNKNOWN": Decimal(1)}},
            "notes": tuple("补充说明" + "😀" * 80 + str(i) for i in range(20)),
        }
    )
    parts = apple_business_digest_content("😀" * 2000, [snap])
    assert parts == apple_business_digest_content("😀" * 2000, [snap])
    assert len(parts) > 1 and all(len(part.encode("utf-16-le")) // 2 <= 2000 for part in parts)
    assert "可见部分" in "\n".join(parts) and "UNKNOWN" in "\n".join(parts)
    assert all("2026-10-25" in part and "USD" in part for part in parts)


def test_weekly_official_event_counts_are_additive_but_unique_totals_are_not():
    start = date(2026, 10, 19)
    days = [
        daily(
            start + timedelta(days=i),
            impressions=AnalyticsValue(
                value=5, status="available", source="App Store Discovery and Engagement Standard"
            ),
        )
        for i in range(7)
    ]
    rendered = text(days, period="weekly")
    assert "曝光：35" in rendered and "事件次数" in rendered


def test_incomplete_status_and_mismatched_currency_never_produce_rate():
    current = daily(sales_usd=5)
    previous = daily(
        date(2026, 10, 24),
        sales_usd=AnalyticsValue(value=1, status="available", currency="CNY", source="Apple"),
    )
    rendered = text([current], comparison=[previous])
    assert "+400.0%" not in rendered
    assert "USD 5.00" in rendered
    invalid = AnalyticsValue(value=5, status="available", currency="CNY", source="Apple")
    earlier = invalid.model_copy(update={"value": Decimal(1)})
    rendered = text([daily(sales_usd=invalid)], comparison=[daily(date(2026, 10, 24), sales_usd=earlier)])
    assert "缺少 USD 口径" in rendered and "+400.0%" not in rendered


def test_unknown_source_cannot_claim_comparable_change():
    current = daily(first_downloads=AnalyticsValue(value=2, status="available"))
    previous = daily(date(2026, 10, 24), first_downloads=AnalyticsValue(value=1, status="available"))
    assert "+100.0%" not in text([current], comparison=[previous])


def test_daily_week_comparison_uses_prior_same_day_and_never_fills_missing_history():
    current = daily(first_downloads=3)
    previous_week = daily(date(2026, 10, 18), first_downloads=2)
    rendered = text([current], week_comparison=[previous_week])
    assert "较上周同日 +50.0%" in rendered and "2026-10-18" in rendered
    assert "上周同日：历史不足" in text([current])
    assert "+50.0%" not in text([current], week_comparison=[daily(date(2026, 10, 17), first_downloads=2)])
