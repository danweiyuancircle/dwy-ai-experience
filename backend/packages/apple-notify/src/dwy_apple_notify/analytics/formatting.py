"""中文经营摘要；不将缺失、去重人数或订阅存量当作可累计流量。"""

from datetime import timedelta
from decimal import Decimal

from .models import AnalyticsValue

_LABELS = {
    "first_downloads": "首次下载",
    "redownloads": "重新下载",
    "impressions": "曝光",
    "page_views": "产品页访问",
    "store_conversion_rate": "商店转化率",
    "sales_usd": "销售额",
    "proceeds_usd": "收益",
    "refunds_usd": "退款金额",
    "refund_count": "负购买数量（非退款总笔数）",
    "paid_subscriptions": "付费订阅存量",
    "paid_offer_subscriptions": "付费优惠订阅存量",
    "free_trials": "免费试用存量",
    "paid_starts": "付费开始",
    "offer_conversions": "优惠转正",
    "renewals": "续订",
    "voluntary_churn": "主动流失",
    "involuntary_churn": "被动流失",
    "billing_issues": "账单异常存量",
    "billing_recoveries": "账单恢复",
    "trial_starts": "试用开始",
    "review_count": "评论数（UTC 创建日）",
    "low_star_reviews": "低星评论（UTC 创建日，1–2 星）",
}
_STOCKS = {"paid_subscriptions", "paid_offer_subscriptions", "free_trials", "billing_issues"}
_NONADDITIVE = {"impressions", "page_views", "store_conversion_rate"}
_DISCOVERY_COUNTS = "App Store Discovery and Engagement Standard"
_DIMENSIONS = {
    "download_territories": "下载地区",
    "proceeds_territories": "收益地区（USD）",
    "download_sources": "获客来源",
}


def _bounded(value, limit=1800):
    encoded = str(value).replace("@", "＠").replace("\r", " ").replace("\n", " ").encode("utf-16-le")
    return (
        encoded.decode("utf-16-le")
        if len(encoded) <= limit * 2
        else encoded[: (limit - 1) * 2].decode("utf-16-le", errors="ignore") + "…"
    )


def _complete(snapshots, length):
    return len(snapshots) == length and all(
        right.report_date == left.report_date + timedelta(days=1)
        for left, right in zip(snapshots, snapshots[1:], strict=False)
    )


def _available(value):
    return value.status == "available" and value.value is not None


def _same_basis(values):
    return (
        bool(values)
        and all(_available(v) and v.source for v in values)
        and len({(v.source, v.currency) for v in values}) == 1
    )


def _event_counts(snapshots, key):
    return key in ("impressions", "page_views") and all(
        snap.metrics.get(key, AnalyticsValue()).source == _DISCOVERY_COUNTS for snap in snapshots
    )


def _metric(snapshots, key, weekly):
    values = [snap.metrics.get(key, AnalyticsValue()) for snap in snapshots]
    if not weekly or key in _STOCKS:
        return values[-1]
    if key in _NONADDITIVE and not _event_counts(snapshots, key):
        return AnalyticsValue(source=values[-1].source)
    if _complete(snapshots, 7) and _same_basis(values):
        return AnalyticsValue(
            value=sum((v.value for v in values), Decimal(0)),
            status="available",
            source=values[0].source,
            currency=values[0].currency,
        )
    return AnalyticsValue(status="pending" if any(v.status == "pending" for v in values) else "unavailable")


def _number(value, key):
    if key.endswith("_usd"):
        return f"USD {value.value:.2f}"
    return f"{value.value:f}" + ("%" if key == "store_conversion_rate" else "")


def _change(current, previous, *, stock=False, label="变化"):
    if not _same_basis([current, previous]):
        return ""
    delta = current.value - previous.value
    if stock:
        return f"；较期初 {delta:+f}"
    if previous.value == 0:
        return f"；{label}：基期为 0，百分比不适用"
    return f"；{label} {delta / abs(previous.value) * 100:+.1f}%"


def apple_business_digest_content(
    app_name, snapshots, *, period="daily", comparison=(), week_comparison=()
) -> list[str]:
    """逐项展示数值或无数据，每段 ≤2000 UTF-16 码元；周流量只累计连续完整七天。"""
    snapshots, previous = (
        sorted(snapshots, key=lambda s: s.report_date),
        sorted(comparison, key=lambda s: s.report_date),
    )
    previous_week = sorted(week_comparison, key=lambda s: s.report_date)
    weekly = period == "weekly"
    if period not in ("daily", "weekly") or not _complete(snapshots, 7 if weekly else 1):
        raise ValueError("Analytics digest requires a complete contiguous period")
    if len({s.app_id for s in snapshots + previous + previous_week}) != 1:
        raise ValueError("Analytics digest cannot combine applications")
    start, end = snapshots[0].report_date, snapshots[-1].report_date
    prior_length = 7 if weekly else 1
    comparable = _complete(previous, prior_length) and previous[-1].report_date == start - timedelta(days=1)
    endpoint = bool(previous) and previous[-1].report_date == start - timedelta(days=1)
    week_comparable = (
        not weekly and _complete(previous_week, 1) and previous_week[0].report_date == end - timedelta(days=7)
    )
    title = f"**【Apple 经营{'周报' if weekly else '日报'}】**"
    header_lines = [
        title,
        "应用：" + _bounded(app_name, 128),
        f"统计日：{start.isoformat()}" + (f" 至 {end.isoformat()}（连续七天）" if weekly else ""),
    ]
    lines = []
    comparison_used = week_comparison_used = money_present = False
    for key, label in _LABELS.items():
        value = _metric(snapshots, key, weekly)
        if not _available(value) or (key.endswith("_usd") and value.currency != "USD"):
            lines.append(f"{label}：无数据")
            continue
        rendered = _number(value, key)
        money_present |= key.endswith("_usd")
        if _event_counts(snapshots, key):
            rendered += "（事件次数，非独立设备）"
        if weekly and key in _STOCKS:
            rendered += "（期末快照）"
        if comparable or (weekly and key in _STOCKS and endpoint):
            change = _change(value, _metric(previous, key, weekly), stock=weekly and key in _STOCKS)
            rendered += change
            comparison_used |= bool(change)
        if week_comparable:
            change = _change(value, _metric(previous_week, key, False), label="较上周同日")
            rendered += change
            week_comparison_used |= bool(change)
        lines.append(f"{label}：{rendered}")
    for key, label in _DIMENSIONS.items():
        prefix = label + " Top 3（可见部分，不代表全量覆盖）："
        dimensions = [snap.breakdowns.get(key) for snap in snapshots]
        if any(d is None for d in dimensions):
            lines.append(prefix + "无数据")
            continue
        totals = {}
        for dimension in dimensions:
            for name, count in dimension.items():
                totals[name] = totals.get(name, Decimal(0)) + count
        top = sorted(totals, key=lambda name: (-totals[name], name))[:3]
        if not top:
            lines.append(prefix + "无数据")
            continue
        top += [
            name
            for name in sorted(totals)
            if name.upper() in ("OTHER", "OTHERS", "UNKNOWN", "其他", "未知") and name not in top
        ]
        lines.append(
            prefix
            + "；".join(f"{_bounded(name, 64)} {totals[name]:f}" for name in top)
        )
    # 内部状态和诊断备注留在快照，缺失字段在正文统一显示无数据。
    if money_present:
        header_lines.append("金额：Apple 报表 USD 估算，非最终到账。")
    if comparison_used:
        lines.insert(0, f"比较期间：{previous[0].report_date} 至 {previous[-1].report_date}")
    if week_comparison_used:
        lines.insert(0, f"上周同日：{previous_week[0].report_date}")
    # 每段自带应用、统计日及币种，单段重试或晚到也可独立阅读。
    header = "\n".join(header_lines)
    budget = 2000 - len(header.encode("utf-16-le")) // 2 - 1
    parts, current = [], header
    for line in lines:
        line = _bounded(line, budget)
        candidate = current + "\n" + line
        if len(candidate.encode("utf-16-le")) // 2 > 2000:
            parts.append(current)
            current = header + "\n" + line
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts
