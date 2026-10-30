"""日报和周报不得把缺失、存量或独立设备当作可相加流量。"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from dwy_apple_notify.analytics.formatting import apple_business_digest_content
from dwy_apple_notify.analytics.models import AnalyticsValue, AppleBusinessSnapshot


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


def test_daily_keeps_values_and_safe_comparison_without_source_noise():
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
    assert "续订：无数据" in rendered and "待发布" not in rendered
    assert "不可用" not in rendered and "来源：" not in rendered
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
    assert "曝光：无数据" in rendered
    partial = days[:-1] + [daily(start + timedelta(days=6), paid_subscriptions=16)]
    assert "首次下载：无数据" in text(partial, period="weekly")


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
    snap = daily(**{key: 123456789012345678 for key in (
        "first_downloads", "redownloads", "paid_subscriptions", "paid_offer_subscriptions",
        "free_trials", "paid_starts", "offer_conversions", "renewals", "voluntary_churn",
        "involuntary_churn", "billing_issues", "billing_recoveries", "trial_starts",
        "sales_usd", "proceeds_usd", "refunds_usd", "refund_count",
    )}).model_copy(
        update={
            "breakdowns": {
                key: {"😀" * 80 + str(i): Decimal(i) for i in range(4)} | {"UNKNOWN": Decimal(1)}
                for key in ("download_territories", "proceeds_territories", "download_sources")
            },
            "notes": tuple("补充说明" + "😀" * 80 + str(i) for i in range(20)),
        }
    )
    previous = snap.model_copy(update={
        "report_date": date(2026, 10, 24),
        "metrics": {key: value.model_copy(update={"value": Decimal(1)})
                    for key, value in snap.metrics.items()},
    })
    comparisons = {"comparison": [previous], "week_comparison": [
        previous.model_copy(update={"report_date": date(2026, 10, 18)})]}
    parts = apple_business_digest_content("😀" * 2000, [snap], **comparisons)
    assert parts == apple_business_digest_content("😀" * 2000, [snap], **comparisons)
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
    assert "销售额：无数据" in rendered and "+400.0%" not in rendered


def test_unknown_source_cannot_claim_comparable_change():
    current = daily(first_downloads=AnalyticsValue(value=2, status="available"))
    previous = daily(date(2026, 10, 24), first_downloads=AnalyticsValue(value=1, status="available"))
    assert "+100.0%" not in text([current], comparison=[previous])


def test_daily_week_comparison_uses_prior_same_day_and_never_fills_missing_history():
    current = daily(first_downloads=3)
    previous_week = daily(date(2026, 10, 18), first_downloads=2)
    rendered = text([current], week_comparison=[previous_week])
    assert "较上周同日 +50.0%" in rendered and "2026-10-18" in rendered
    assert "上周同日" not in text([current])
    assert "+50.0%" not in text([current], week_comparison=[daily(date(2026, 10, 17), first_downloads=2)])


def test_daily_shows_missing_metrics_and_empty_dimensions_but_keeps_real_zero():
    """缺失值逐项显示无数据，已有的零必须保留。"""
    snapshot = daily(
        first_downloads=0,
        sales_usd=0,
        paid_starts=AnalyticsValue(status="not_applicable"),
        free_trials=AnalyticsValue(status="unavailable"),
        renewals=AnalyticsValue(status="pending"),
        trial_starts=AnalyticsValue(status="available"),
    ).model_copy(update={"breakdowns": {"download_territories": {}, "download_sources": {}}})
    rendered = text([snapshot])
    assert "首次下载：0" in rendered and "销售额：USD 0.00" in rendered
    assert "USD 估算" in rendered
    assert "待发布" not in rendered and "来源：" not in rendered
    for label in ("付费开始", "免费试用存量", "续订", "试用开始", "商店转化率"):
        assert f"{label}：无数据" in rendered
    for label in ("下载地区", "收益地区（USD）", "获客来源"):
        assert f"{label} Top 3（可见部分，不代表全量覆盖）：无数据" in rendered


@pytest.mark.parametrize("period", ["daily", "weekly"])
@pytest.mark.parametrize("status", ["pending", "unavailable", "not_applicable", "available"])
def test_empty_report_lists_every_field_as_no_data(period, status):
    """日报周报均逐项展示缺失值，状态或空值不能冒充零。"""
    start = date(2026, 10, 25)
    snapshots = [daily(start + timedelta(days=index), renewals=AnalyticsValue(status=status))
                 for index in range(7 if period == "weekly" else 1)]
    rendered = text(snapshots, period=period)
    assert len(rendered.splitlines()) == 28
    assert "2026-10-25" in rendered and "工具" in rendered
    assert rendered.count("：无数据") == 25
    assert "续订：无数据" in rendered and "收益：无数据" in rendered
    assert all(snapshot.metrics["renewals"].status == status for snapshot in snapshots)
    for hidden in ("待发布", "暂无可展示", "来源：", "比较期间", "上周同日"):
        assert hidden not in rendered


def test_internal_notes_are_hidden_and_dimensions_neutralize_mentions():
    """诊断备注保留在快照中，不向用户广播内部英文状态。"""
    snapshot = daily(first_downloads=1).model_copy(update={
        "notes": ("Unique Counts are not summed", "Apple may correct recent reports"),
        "breakdowns": {"download_sources": {"@everyone": Decimal(1)}},
    })
    rendered = "\n".join(apple_business_digest_content("@here", [snapshot]))
    assert "@" not in rendered and "＠everyone" in rendered
    assert "Unique Counts" not in rendered and "说明：" not in rendered


def test_comparison_headers_only_appear_for_rendered_same_basis_changes():
    """日期相邻仍不足以比较，至少一项同口径历史存在才显示比较期间。"""
    current = daily(first_downloads=2)
    previous = daily(date(2026, 10, 24), first_downloads=AnalyticsValue(
        value=1, status="available", source="Other"))
    assert "比较期间" not in text([current], comparison=[previous])
    assert "比较期间" in text([current], comparison=[daily(date(2026, 10, 24), first_downloads=1)])
