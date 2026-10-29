from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from dwy_webhooks.analytics.metrics import aggregate_reports
from dwy_webhooks.analytics.models import AnalyticsValue, AppleBusinessSnapshot

DAY = date(2026, 10, 20)


def test_snapshot_values_are_typed_and_frozen():
    value = AnalyticsValue(value=Decimal("1.25"), status="available", currency="USD")
    snapshot = AppleBusinessSnapshot(app_id="123", report_date=DAY, metrics={"sales_usd": value})
    assert snapshot.metrics["sales_usd"].value == Decimal("1.25")
    with pytest.raises(ValidationError):
        value.status = "pending"


def test_official_download_and_purchase_fields_partial_refunds_and_sources():
    result = aggregate_reports(
        "123",
        DAY,
        {
            "App Downloads Standard": [
                {
                    "Date": str(DAY),
                    "App Apple Identifier": "123",
                    "Download Type": "First-time Download",
                    "Counts": "3",
                    "Territory": "USA",
                    "Source Type": "App Store search",
                },
                {
                    "Date": str(DAY),
                    "App Apple Identifier": "123",
                    "Download Type": "Redownload",
                    "Counts": "2",
                    "Territory": "USA",
                    "Source Type": "App Store browse",
                },
            ],
            "App Store Purchases Standard": [
                {
                    "Date": str(DAY),
                    "App Apple Identifier": "123",
                    "Purchases": "2",
                    "Sales in USD": "4.50",
                    "Proceeds in USD": "3.15",
                    "Territory": "USA",
                    "Paying Users": "2",
                },
                {
                    "Date": str(DAY),
                    "App Apple Identifier": "123",
                    "Purchases": "0",
                    "Sales in USD": "-0.50",
                    "Proceeds in USD": "-0.35",
                    "Territory": "USA",
                    "Paying Users": "1",
                },
            ],
        },
    )
    assert result.metrics["first_downloads"].value == 3
    assert result.metrics["redownloads"].value == 2
    assert result.metrics["sales_usd"].value == Decimal("4.00")
    assert result.metrics["refunds_usd"].value == Decimal("0.50")
    assert result.metrics["refund_count"].value == 0
    assert result.metrics["store_conversion_rate"].status == "unavailable"
    assert "Paying Users" not in result.metrics
    assert result.breakdowns["download_territories"] == {"USA": Decimal(5)}
    assert result.metrics["sales_usd"].source == "App Store Purchases Standard"


@pytest.mark.parametrize("bad", ["NaN", "Infinity", "1e99999", "garbage"])
def test_invalid_decimal_is_a_safe_collection_error(bad):
    from dwy_webhooks.analytics.models import AnalyticsCollectionError

    with pytest.raises(AnalyticsCollectionError, match="analytics_invalid_report"):
        aggregate_reports(
            "123",
            DAY,
            {
                "App Store Purchases Standard": [
                    {
                        "Date": str(DAY),
                        "App Apple Identifier": "123",
                        "Purchases": "1",
                        "Sales in USD": bad,
                        "Proceeds in USD": "1",
                        "Territory": "USA",
                    }
                ]
            },
        )


def test_verified_subscription_stocks_and_events_and_discovery_counts():
    from dwy_webhooks.analytics.metrics import DISCOVERY, EVENTS, STATE

    def state(label, group, count):
        return {
            "Date": str(DAY),
            "App Apple Identifier": "123",
            "State Metric": label,
            "State Metric Grouping": group,
            "Counts": str(count),
        }

    def event(group, subtype, count):
        return {
            "Event Date": str(DAY),
            "App Apple Identifier": "123",
            "Event Grouping": group,
            "Event Sub Type": subtype,
            "Counts": str(count),
        }

    result = aggregate_reports(
        "123",
        DAY,
        {
            STATE: [
                state("Full price", "Paid plans", 10),
                state("Paid offers", "Subscription offers", 2),
                state("Free trials", "Subscription offers", 3),
                state("Billing retry", "Billing issue", 4),
            ],
            EVENTS: [
                event("Paid Subscription Starts", "Full Price Subscription Starts", 5),
                event("Offer Starts", "Free Trial Starts", 6),
                event("Renewals", "Full Price Renewals", 7),
                event("Paid Subscriptions from Offers", "Full Price from Free Trial", 8),
                event("Voluntary Churn", "Voluntary Churn from Full Price", 9),
                event("Involuntary Churn", "Involuntary Churn from Full Price", 10),
                event("Recoveries from Billing Issue", "Full Price Recoveries from Grace Period", 11),
            ],
            DISCOVERY: [
                {
                    "Date": str(DAY),
                    "App Apple Identifier": "123",
                    "Event": "Impression",
                    "Page Type": "No page",
                    "Counts": "100",
                    "Unique Counts": "1",
                },
                {
                    "Date": str(DAY),
                    "App Apple Identifier": "123",
                    "Event": "Page view",
                    "Page Type": "Product page",
                    "Counts": "20",
                    "Unique Counts": "1",
                },
            ],
        },
    )
    expected = {
        "paid_subscriptions": 10,
        "paid_offer_subscriptions": 2,
        "free_trials": 3,
        "billing_issues": 4,
        "paid_starts": 5,
        "trial_starts": 6,
        "renewals": 7,
        "offer_conversions": 8,
        "voluntary_churn": 9,
        "involuntary_churn": 10,
        "billing_recoveries": 11,
        "impressions": 100,
        "page_views": 20,
    }
    assert {k: result.metrics[k].value for k in expected} == expected


def test_unknown_event_category_does_not_claim_zero_and_missing_rows_stay_unknown():
    from dwy_webhooks.analytics.metrics import DOWNLOADS, EVENTS

    snapshot = aggregate_reports(
        "123",
        DAY,
        {
            EVENTS: [
                {
                    "Event Date": str(DAY),
                    "App Apple Identifier": "123",
                    "Event Grouping": "Future Event",
                    "Event Sub Type": "Future",
                    "Counts": "8",
                }
            ],
            DOWNLOADS: [],
        },
    )
    assert snapshot.metrics["paid_starts"].status == "unavailable"
    assert snapshot.metrics["first_downloads"].value is None
    assert any("unrecognized" in n for n in snapshot.notes)


def test_product_page_views_exclude_developer_privacy_and_event_pages():
    from dwy_webhooks.analytics.metrics import DISCOVERY

    rows = [
        {
            "Date": str(DAY),
            "App Apple Identifier": "123",
            "Event": "Page view",
            "Page Type": page,
            "Counts": str(count),
        }
        for page, count in (
            ("Product page", 3),
            ("Developer page", 10),
            ("App privacy", 20),
            ("In-app event", 30),
            ("App version history", 40),
        )
    ]
    result = aggregate_reports("123", DAY, {DISCOVERY: rows})
    assert result.metrics["page_views"].value == 3
    assert any("Product page" in note for note in result.notes)


def test_refund_quantity_note_excludes_partial_refund_transaction_count():
    result = aggregate_reports("123", DAY, {})
    assert any("refund_count" in note and "partial refund" in note for note in result.notes)
