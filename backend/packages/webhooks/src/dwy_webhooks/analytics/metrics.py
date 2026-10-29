"""Aggregate verified Apple Analytics report fields; unique people are never summed."""

from datetime import date
from decimal import Decimal, InvalidOperation

from .models import AnalyticsCollectionError, AnalyticsValue, AppleBusinessSnapshot

DOWNLOADS = "App Downloads Standard"
DISCOVERY = "App Store Discovery and Engagement Standard"
PURCHASES = "App Store Purchases Standard"
STATE = "App Store Subscription State Report Standard"
EVENTS = "App Store Subscription Event Report Standard"
REPORT_NAMES = (DOWNLOADS, DISCOVERY, PURCHASES, STATE, EVENTS)
METRIC_KEYS = (
    "first_downloads",
    "redownloads",
    "impressions",
    "page_views",
    "store_conversion_rate",
    "sales_usd",
    "proceeds_usd",
    "refunds_usd",
    "refund_count",
    "paid_subscriptions",
    "paid_offer_subscriptions",
    "free_trials",
    "paid_starts",
    "offer_conversions",
    "renewals",
    "voluntary_churn",
    "involuntary_churn",
    "billing_issues",
    "billing_recoveries",
    "trial_starts",
)
_GROUPS = {
    DOWNLOADS: ("first_downloads", "redownloads"),
    DISCOVERY: ("impressions", "page_views"),
    PURCHASES: ("sales_usd", "proceeds_usd", "refunds_usd", "refund_count"),
    STATE: ("paid_subscriptions", "paid_offer_subscriptions", "free_trials", "billing_issues"),
    EVENTS: (
        "paid_starts",
        "offer_conversions",
        "renewals",
        "voluntary_churn",
        "involuntary_churn",
        "billing_recoveries",
        "trial_starts",
    ),
}
_EVENT_GROUPS = {
    "Offer Starts",
    "Offer Renewals",
    "Paid Subscriptions from Offers",
    "Paid Subscription Starts",
    "Renewals",
    "Commitment-Based Payments",
    "Entered Billing Issue",
    "Recoveries from Billing Issue",
    "Involuntary Churn",
    "Voluntary Churn",
    "Exits",
    "Extensions",
}
_STATES = {
    "Free trials",
    "Paid offers",
    "Full price",
    "Preserved price",
    "Contingent price",
    "Grace period",
    "Billing retry",
    "Suspended",
    "Voluntarily churned",
    "Involuntarily churned",
}


def _number(row: dict[str, str], name: str, *, integer: bool = False, negative: bool = False) -> Decimal:
    try:
        raw = row[name]
        if not isinstance(raw, str) or not 1 <= len(raw) <= 64:
            raise ValueError
        value = Decimal(raw)
        if (
            not value.is_finite()
            or value.copy_abs() > Decimal("1e18")
            or not negative
            and value < 0
            or integer
            and value != value.to_integral_value()
        ):
            raise ValueError
        return value
    except (KeyError, TypeError, ValueError, InvalidOperation):
        raise AnalyticsCollectionError("analytics_invalid_report") from None


def aggregate_reports(
    app_id: str,
    report_date: date,
    reports: dict[str, list[dict[str, str]]],
    *,
    pending: tuple[str, ...] = (),
    notes: tuple[str, ...] = (),
) -> AppleBusinessSnapshot:
    """Inputs contain one corrected version per report; no rows means unknown, not zero."""
    metrics = {key: AnalyticsValue() for key in METRIC_KEYS}
    breakdowns = {key: {} for key in ("download_territories", "proceeds_territories", "download_sources")}
    messages = list(notes)
    for source in pending:
        for key in _GROUPS.get(source, ()):
            metrics[key] = AnalyticsValue(
                status="pending", source=source, currency="USD" if key.endswith("_usd") else None
            )
    for source, rows in reports.items():
        if source not in _GROUPS:
            continue
        totals = {key: Decimal(0) for key in _GROUPS[source]}
        matching = 0
        unrecognized = False
        for row in rows:
            try:
                day = date.fromisoformat(row["Event Date" if source == EVENTS else "Date"])
                if row["App Apple Identifier"] != app_id or day != report_date:
                    continue
                matching += 1
                if source == PURCHASES:
                    sales = _number(row, "Sales in USD", negative=True)
                    proceeds = _number(row, "Proceeds in USD", negative=True)
                    count = _number(row, "Purchases", integer=True, negative=True)
                    totals["sales_usd"] += sales
                    totals["proceeds_usd"] += proceeds
                    totals["refunds_usd"] += max(-sales, Decimal(0))
                    totals["refund_count"] += max(-count, Decimal(0))
                    territory = row["Territory"]
                    breakdowns["proceeds_territories"][territory] = (
                        breakdowns["proceeds_territories"].get(territory, Decimal(0)) + proceeds
                    )
                else:
                    count = _number(row, "Counts", integer=True)
                    if source == DOWNLOADS:
                        kind = row["Download Type"]
                        if kind not in {
                            "First-time Download",
                            "Redownload",
                            "Manual update",
                            "Auto-update",
                            "Restore",
                        }:
                            unrecognized = True
                        key = {"First-time Download": "first_downloads", "Redownload": "redownloads"}.get(
                            kind
                        )
                        if key:
                            totals[key] += count
                            for output, field in (
                                ("download_territories", "Territory"),
                                ("download_sources", "Source Type"),
                            ):
                                label = row[field]
                                breakdowns[output][label] = breakdowns[output].get(label, Decimal(0)) + count
                    elif source == DISCOVERY:
                        if row["Event"] not in {"Impression", "Page view", "Tap"}:
                            unrecognized = True
                        if row["Event"] == "Impression":
                            totals["impressions"] += count
                        if row["Event"] == "Page view" and row["Page Type"] == "Product page":
                            totals["page_views"] += count
                    elif source == STATE:
                        state, group = row["State Metric"], row["State Metric Grouping"]
                        if state not in _STATES or group not in {
                            "Subscription offers",
                            "Paid plans",
                            "Billing issue",
                            "Churned",
                        }:
                            unrecognized = True
                        if group == "Paid plans":
                            totals["paid_subscriptions"] += count
                        if group == "Billing issue":
                            totals["billing_issues"] += count
                        key = {"Free trials": "free_trials", "Paid offers": "paid_offer_subscriptions"}.get(
                            state
                        )
                        if key:
                            totals[key] += count
                    elif source == EVENTS:
                        if row["Event Grouping"] not in _EVENT_GROUPS:
                            unrecognized = True
                        key = {
                            "Paid Subscription Starts": "paid_starts",
                            "Paid Subscriptions from Offers": "offer_conversions",
                            "Renewals": "renewals",
                            "Voluntary Churn": "voluntary_churn",
                            "Involuntary Churn": "involuntary_churn",
                            "Recoveries from Billing Issue": "billing_recoveries",
                        }.get(row["Event Grouping"])
                        if key:
                            totals[key] += count
                        if row["Event Sub Type"] == "Free Trial Starts":
                            totals["trial_starts"] += count
            except (KeyError, ValueError, TypeError):
                raise AnalyticsCollectionError("analytics_invalid_report") from None
        if unrecognized:
            for key in _GROUPS[source]:
                metrics[key] = AnalyticsValue(source=source, currency="USD" if key.endswith("_usd") else None)
            messages.append(source + ": unrecognized event category; affected metrics are unavailable")
        elif matching:
            for key, value in totals.items():
                metrics[key] = AnalyticsValue(
                    value=value,
                    status="available",
                    source=source,
                    currency="USD" if key.endswith("_usd") else None,
                )
        else:
            messages.append(
                source + ": no matching rows; missing or privacy-suppressed values are unavailable"
            )
    messages.extend(
        (
            "UTC report date; Apple may correct recent reports",
            "USD sales and proceeds are Apple estimates; refund USD is the magnitude of negative sales",
            "refund_count is negative Purchases quantity, excluding partial refund transaction counts",
            "Unique Counts and Paying Users are not summed; official store conversion rate is unavailable",
            "page_views counts only Page view events with Page Type Product page",
            "Paid subscriptions are Paid plans; paid offers and free trials are separate stocks",
        )
    )
    return AppleBusinessSnapshot(
        app_id=app_id, report_date=report_date, metrics=metrics, breakdowns=breakdowns, notes=tuple(messages)
    )
