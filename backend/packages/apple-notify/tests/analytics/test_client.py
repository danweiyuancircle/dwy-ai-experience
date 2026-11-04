import asyncio
import gzip
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, call

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from dwy_apple_notify.analytics.client import AppleAnalyticsClient
from dwy_apple_notify.analytics.models import AnalyticsApp, AnalyticsCollectionError, AppleAnalyticsConfig

DAY = date(2026, 10, 20)
ORIGIN = "https://api.appstoreconnect.apple.com"
DOWNLOAD = "https://asp-reporting.s3.us-west-2.amazonaws.com/report.gz?signature=private"


def config():
    key = (
        ec.generate_private_key(ec.SECP256R1())
        .private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
        .decode()
    )
    return AppleAnalyticsConfig(
        apps={"123": AnalyticsApp(name="Demo")},
        issuer_id="12345678-1234-1234-1234-123456789012",
        key_id="ABCDEFGHIJ",
        private_key=key,
    )


def collection(data, next_url=None):
    return {"data": data, "links": {"next": next_url}}


@pytest.mark.asyncio
async def test_collect_discovers_ongoing_and_all_segments_latest_date_replaces():
    seen = []

    async def transport(request):
        seen.append(request)
        path = request.url.path
        if request.url.host.endswith("amazonaws.com"):
            assert "authorization" not in request.headers
            n = {"old": 2, "new1": 3, "new2": 4}[path.split("/")[1]]
            raw = (
                "Date\tApp Apple Identifier\tDownload Type\tCounts\tTerritory\tSource Type\n"
                f"{DAY}\t123\tFirst-time Download\t{n}\tUSA\tApp Store search\n"
            ).encode()
            return httpx.Response(200, stream=httpx.ByteStream(gzip.compress(raw)))
        assert request.headers["authorization"].startswith("Bearer ")
        if path.endswith("/analyticsReportRequests"):
            return httpx.Response(
                200,
                json=collection(
                    [
                        {
                            "id": "req",
                            "type": "analyticsReportRequests",
                            "attributes": {"accessType": "ONGOING", "stoppedDueToInactivity": False},
                        }
                    ]
                ),
            )
        if path.endswith("/reports"):
            return httpx.Response(
                200,
                json=collection(
                    [
                        {
                            "id": "rep",
                            "type": "analyticsReports",
                            "attributes": {"name": "App Downloads Standard"},
                        }
                    ]
                ),
            )
        if path.endswith("/instances"):
            return httpx.Response(
                200,
                json=collection(
                    [
                        {
                            "id": x,
                            "type": "analyticsReportInstances",
                            "attributes": {"granularity": "DAILY", "processingDate": d},
                        }
                        for x, d in [("old", "2026-10-21"), ("new", "2026-10-22")]
                    ]
                ),
            )
        if path.endswith("/segments"):
            names = ["old"] if "/old/" in path else ["new1", "new2"]
            return httpx.Response(
                200,
                json=collection(
                    [
                        {
                            "id": n,
                            "type": "analyticsReportSegments",
                            "attributes": {"url": DOWNLOAD.replace("report.gz", n + "/report.gz")},
                        }
                        for n in names
                    ]
                ),
            )
        raise AssertionError(path)

    injected = httpx.AsyncClient(transport=httpx.MockTransport(transport))
    client = AppleAnalyticsClient(config(), client=injected)
    snapshot = await client.collect("123", DAY)
    assert snapshot.metrics["first_downloads"].value == 7
    assert snapshot.metrics["sales_usd"].status == "unavailable"
    assert len([r for r in seen if r.url.host.endswith("amazonaws.com")]) == 3
    await client.aclose()
    assert not injected.is_closed
    await injected.aclose()


@pytest.mark.asyncio
async def test_collect_never_creates_and_initialize_explicitly_posts():
    methods = []

    async def transport(request):
        methods.append(request.method)
        if request.method == "POST":
            assert b"ONGOING" in request.content
            return httpx.Response(201, json={"data": {"id": "created", "type": "analyticsReportRequests"}})
        return httpx.Response(200, json=collection([]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        client = AppleAnalyticsClient(config(), client=http)
        snapshot = await client.collect("123", DAY)
        assert all(v.status == "pending" for k, v in snapshot.metrics.items() if k != "store_conversion_rate")
        assert methods == ["GET"]
        assert await client.initialize("123") == "created"
        assert methods[-1] == "POST"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", [httpx.ConnectError, httpx.ReadTimeout, httpx.ReadError, httpx.RemoteProtocolError]
)
async def test_collect_retries_transient_get_failures_before_returning_snapshot(monkeypatch, failure):
    """瞬断在当前请求内恢复，不能先把整轮采集判成失败。"""
    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    attempts = 0

    async def transport(request):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise failure("private-request-url", request=request)
        return httpx.Response(200, json=collection([]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        snapshot = await AppleAnalyticsClient(config(), client=http).collect("123", DAY)
    assert snapshot.app_id == "123" and snapshot.report_date == DAY
    assert snapshot.metrics["first_downloads"].status == "pending"
    assert attempts == 3
    assert sleep.await_args_list == [call(1), call(2)]


@pytest.mark.asyncio
async def test_collect_retries_read_failure_after_partial_response_without_reusing_bytes(monkeypatch):
    """断流前的字节必须丢弃，重读完整响应后再解析。"""
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    attempts = 0
    closed = []

    class BrokenStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"data":['
            raise httpx.ReadError("private-response-url")

        async def aclose(self):
            closed.append(True)

    async def transport(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(200, stream=BrokenStream())
        return httpx.Response(200, json=collection([]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        snapshot = await AppleAnalyticsClient(config(), client=http).collect("123", DAY)
    assert snapshot.report_date == DAY
    assert attempts == 2 and closed == [True]


@pytest.mark.asyncio
async def test_collect_stops_after_three_network_failures_with_safe_error(monkeypatch):
    """持续故障仍交给 monitor 告警，且不泄露底层异常正文。"""
    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    attempts = 0

    async def transport(request):
        nonlocal attempts
        attempts += 1
        raise httpx.ReadError("private-request-url", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_request_error$"):
            await AppleAnalyticsClient(config(), client=http).collect("123", DAY)
    assert attempts == 3
    assert sleep.await_args_list == [call(1), call(2)]


@pytest.mark.asyncio
async def test_initialize_does_not_retry_post_after_transport_failure(monkeypatch):
    """创建请求可能已被 Apple 接收，响应丢失时不能自动重复 POST。"""
    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    methods = []

    async def transport(request):
        methods.append(request.method)
        if request.method == "POST":
            raise httpx.ReadTimeout("private-request-url", request=request)
        return httpx.Response(200, json=collection([]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_request_error$"):
            await AppleAnalyticsClient(config(), client=http).initialize("123")
    assert methods == ["GET", "POST"]
    sleep.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,payload,code",
    [
        (401, {}, "analytics_http_error"),
        (503, {}, "analytics_http_error"),
        (200, [], "analytics_invalid_response"),
    ],
)
async def test_collect_does_not_retry_http_or_payload_errors(monkeypatch, status, payload, code):
    """只有传输故障属于本轮重试范围，不重试状态码或无效载荷。"""
    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    attempts = 0

    async def transport(request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(status, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError, match=f"^{code}$"):
            await AppleAnalyticsClient(config(), client=http).collect("123", DAY)
    assert attempts == 1
    sleep.assert_not_awaited()


@pytest.mark.asyncio
async def test_collect_cancellation_during_retry_backoff_propagates(monkeypatch):
    """沿用总采集预算和停机取消，取消后不继续下一次网络请求。"""
    monkeypatch.setattr(asyncio, "sleep", AsyncMock(side_effect=asyncio.CancelledError))
    attempts = 0

    async def transport(request):
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError("private-request-url", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(asyncio.CancelledError):
            await AppleAnalyticsClient(config(), client=http).collect("123", DAY)
    assert attempts == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failures,event,completed", [(2, "analytics.daily", 1), (3, "analytics.collection_failed", 0)]
)
async def test_monitor_only_alerts_after_request_retries_are_exhausted(
    monkeypatch,
    tmp_path,
    failures,
    event,
    completed,
):
    """真实采集和 outbox 链路中，瞬断恢复只生成日报，持续故障仍告警。"""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from dwyeapi.database import create_async_engine_factory, create_session_factory
    from sqlalchemy import MetaData, select

    from dwy_apple_notify.analytics.service import AnalyticsMonitor
    from dwy_apple_notify.analytics.storage import AnalyticsStore, build_analytics_tables

    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    attempts = 0

    async def transport(request):
        nonlocal attempts
        attempts += 1
        if attempts <= failures:
            raise httpx.ReadTimeout("private-request-url", request=request)
        return httpx.Response(200, json=collection([]))

    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{tmp_path / 'retry.db'}")
    metadata = MetaData()
    tables = build_analytics_tables(metadata)
    now = datetime(2026, 11, 4, 8, 30, tzinfo=ZoneInfo("Asia/Shanghai")).timestamp()
    store = AnalyticsStore(create_session_factory(engine), tables, clock=lambda: now)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
            settings = config()
            worker = AnalyticsMonitor(settings, store, AppleAnalyticsClient(settings, client=http))
            assert await worker.run_once() == completed
        async with store.sessions() as db:
            events = (await db.execute(select(tables.deliveries.c.event_type))).scalars().all()
        assert events == [event]
    finally:
        await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event,failure",
    [("connection.connect_tcp", httpx.ConnectTimeout),
     ("connection.start_tls", httpx.ConnectError),
     ("http11.receive_response_headers", httpx.ReadTimeout)],
)
async def test_request_diagnostics_keep_failure_stage_and_redact_trace_details(monkeypatch, event, failure):
    """阶段与类型要能定位首次故障，trace 的敏感参数和异常正文不得进入日志。"""
    import dwy_apple_notify.analytics.client as module

    messages = []
    logger = SimpleNamespace(info=lambda message, *args: messages.append(message % args))
    monkeypatch.setattr(module, "get_logger", lambda name: logger, raising=False)
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    ticks = iter([10.0, 10.25, 11.0, 11.25, 12.0, 12.25])
    monkeypatch.setattr(module, "time", SimpleNamespace(monotonic=lambda: next(ticks)))

    async def transport(request):
        trace = request.extensions.get("trace")
        if trace is not None:
            await trace(event + ".started", {"request": request, "token": "trace-secret"})
            await trace(event + ".failed", {"exception": failure("exception-secret")})
            await trace("http11.response_closed.started", {})
        raise failure("exception-secret", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_request_error$"):
            await AppleAnalyticsClient(config(), client=http)._request(
                "GET", ORIGIN + "/v1/analyticsReports/private-id/instances?cursor=query-secret",
            )
    assert len(messages) == 3
    assert all("operation=instances" in message for message in messages)
    assert all(f"phase={event.rsplit('.', 1)[-1]}" in message for message in messages)
    assert all(f"error_type={failure.__name__}" in message for message in messages)
    assert all("elapsed_ms=250" in message and "outcome=failed" in message for message in messages)
    assert [f"attempt={i}" in message for i, message in enumerate(messages, 1)] == [True, True, True]
    assert len({message.split("request_id=")[1].split()[0] for message in messages}) == 1
    assert not any(word in "\n".join(messages) for word in
                   ("trace-secret", "exception-secret", "query-secret", "private-id", "Bearer", ORIGIN))


@pytest.mark.asyncio
async def test_request_diagnostics_log_recovery_status_without_response_body(monkeypatch):
    """成功重试也应留存同一请求的尝试序号和状态码，便于确认恢复。"""
    import dwy_apple_notify.analytics.client as module

    messages = []
    monkeypatch.setattr(module, "get_logger", lambda name: SimpleNamespace(
        info=lambda message, *args: messages.append(message % args)), raising=False)
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    attempts = 0

    async def transport(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ReadError("exception-secret", request=request)
        return httpx.Response(200, json={"private": "response-secret"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        assert await AppleAnalyticsClient(config(), client=http)._request(
            "GET", ORIGIN + "/v1/apps/private-id/analyticsReportRequests",
        ) == {"private": "response-secret"}
    assert len(messages) == 2
    assert "outcome=failed" in messages[0] and "attempt=1" in messages[0]
    assert "outcome=success" in messages[1] and "attempt=2" in messages[1]
    assert "status=200" in messages[1]
    assert "response-secret" not in "\n".join(messages)


@pytest.mark.asyncio
async def test_pagination_rejects_cross_origin_without_leaking_url():
    async def transport(request):
        return httpx.Response(200, json=collection([], "https://evil.example/private?secret=123"))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_invalid_pagination$"):
            await AppleAnalyticsClient(config(), client=http).collect("123", DAY)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "http://asp-reporting.s3.us-west-2.amazonaws.com/a",
        "https://evil.example/a",
        "https://api.appstoreconnect.apple.com@evil.example/a",
    ],
)
async def test_download_boundary(url):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200))) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_invalid_download$"):
            await AppleAnalyticsClient(config(), client=http)._download(url)


@pytest.mark.asyncio
async def test_download_strips_injected_headers_and_cookies_and_rejects_redirect():
    calls = []

    async def transport(request):
        calls.append(request)
        assert "authorization" not in request.headers
        assert "cookie" not in request.headers
        return httpx.Response(302, headers={"Location": "https://evil.example/signed-secret"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(transport),
        headers={"Authorization": "Bearer account-secret"},
        cookies={"session": "secret"},
    ) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_download_error$"):
            await AppleAnalyticsClient(config(), client=http)._download(DOWNLOAD)
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["compressed", "decompressed", "gzip"])
async def test_download_bounds_and_bad_gzip_are_safe(monkeypatch, kind):
    import dwy_apple_notify.analytics.client as module

    compressed = gzip.compress(b"a" * 1000)
    if kind == "compressed":
        monkeypatch.setattr(module, "_MAX_DOWNLOAD_BYTES", 5)
    elif kind == "decompressed":
        monkeypatch.setattr(module, "_MAX_TSV_BYTES", 5)
    else:
        compressed = b"not gzip, signature=secret"

    async def transport(request):
        return httpx.Response(200, stream=httpx.ByteStream(compressed))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError) as error:
            await AppleAnalyticsClient(config(), client=http)._download(DOWNLOAD)
    assert "secret" not in str(error.value) and "signature" not in str(error.value)


@pytest.mark.parametrize(
    "raw",
    [
        b"Date\tCounts\n2026-10-20\t1",
        b"Date\tDate\tApp Apple Identifier\tEvent\tCounts\n",
        b"\xff",
        b"Date\tApp Apple Identifier\tEvent\tCounts\n2026-10-20\t123\tImpression\t1\textra",
        b"Date\tApp Apple Identifier\tEvent\tCounts\n2026-10-20\t123\tImpression",
    ],
)
def test_tsv_invalid_columns_unicode_and_row_width_fail_safely(raw):
    from dwy_apple_notify.analytics.metrics import DISCOVERY

    with pytest.raises(AnalyticsCollectionError, match="^analytics_invalid_report$"):
        AppleAnalyticsClient._rows(raw, DISCOVERY)


def test_tsv_future_columns_are_ignored():
    from dwy_apple_notify.analytics.metrics import DISCOVERY

    raw = (
        b"Date\tApp Apple Identifier\tEvent\tPage Type\tCounts\tFuture Field\n"
        b"2026-10-20\t123\tImpression\tNo page\t2\tnew"
    )
    assert AppleAnalyticsClient._rows(raw, DISCOVERY)[0]["Counts"] == "2"


@pytest.mark.asyncio
async def test_malformed_attributes_and_pagination_metadata_are_safe():
    async def transport(request):
        return httpx.Response(
            200, json=collection([{"id": "r", "type": "analyticsReportRequests", "attributes": []}])
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_invalid_response$"):
            await AppleAnalyticsClient(config(), client=http).collect("123", DAY)


@pytest.mark.asyncio
async def test_all_paginated_requests_reports_instances_and_segments_are_read():
    paths = []

    async def transport(request):
        paths.append(str(request.url))
        assert request.url.host == "api.appstoreconnect.apple.com"
        if "cursor" not in request.url.params:
            return httpx.Response(
                200,
                json=collection(
                    [{"id": "first", "type": "analyticsReportSegments", "attributes": {"url": DOWNLOAD}}],
                    str(request.url.copy_add_param("cursor", "second")),
                ),
            )
        return httpx.Response(
            200,
            json=collection(
                [{"id": "second", "type": "analyticsReportSegments", "attributes": {"url": DOWNLOAD}}]
            ),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        result = await AppleAnalyticsClient(config(), client=http)._list(
            "/v1/analyticsReportInstances/instance/segments", "analyticsReportSegments"
        )
        assert [x["id"] for x in result] == ["first", "second"]
    assert len(paths) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["cycle", "total", "cursor", "page-cap"])
async def test_pagination_cannot_hide_partial_results(kind, monkeypatch):
    import dwy_apple_notify.analytics.client as module

    async def transport(request):
        item = {
            "id": "req",
            "type": "analyticsReportRequests",
            "attributes": {"accessType": "ONGOING", "stoppedDueToInactivity": False},
        }
        data = collection([item])
        if kind == "total":
            data["meta"] = {"paging": {"total": 2}}
        if kind == "cursor":
            data["meta"] = {"paging": {"nextCursor": "hidden"}}
        if kind in {"cycle", "page-cap"}:
            data["links"]["next"] = str(request.url)
        return httpx.Response(200, json=data)

    if kind == "page-cap":
        monkeypatch.setattr(module, "_MAX_PAGES", 0)
    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError):
            await AppleAnalyticsClient(config(), client=http).collect("123", DAY)


@pytest.mark.parametrize(
    "field,value",
    [
        ("timezone", "not/a/timezone"),
        ("send_hour", 24),
        ("send_minute", 60),
        ("lag_days", 3),
        ("retention_days", 6),
        ("key_id", "invalid"),
        ("issuer_id", "secret"),
        ("apps", {}),
        ("private_key", ""),
    ],
)
def test_config_rejects_invalid_boundaries(field, value):
    from pydantic import ValidationError

    values = config().model_dump()
    values[field] = value
    with pytest.raises(ValidationError):
        AppleAnalyticsConfig(**values)


@pytest.mark.asyncio
async def test_huge_api_response_rejected_without_content_length(monkeypatch):
    import dwy_apple_notify.analytics.client as module

    monkeypatch.setattr(module, "_MAX_PAGE_BYTES", 5)

    async def transport(request):
        return httpx.Response(200, stream=httpx.ByteStream(b'{"data":[],"links":{}}'))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        with pytest.raises(AnalyticsCollectionError, match="^analytics_response_too_large$"):
            await AppleAnalyticsClient(config(), client=http).collect("123", DAY)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "report_name,columns,values,metric",
    [
        (
            "App Downloads Standard",
            "Date\tApp Apple Identifier\tDownload Type\tCounts\tTerritory\tSource Type",
            f"{DAY}\t123\tFirst-time download\t7\tUSA\tApp Store search",
            "first_downloads",
        ),
        (
            "App Store Subscription State Report Standard",
            "Date\tApp Apple Identifier\tState Metric\tState Metric Grouping\tCounts",
            f"{DAY}\t123\tFree trials\tSubscription offers\t7",
            "free_trials",
        ),
        (
            "App Store Subscription Event Report Standard",
            "Event Date\tApp Apple Identifier\tEvent Grouping\tEvent Sub Type\tCounts",
            f"{DAY}\t123\tRenewals\tFull Price Renewals\t7",
            "renewals",
        ),
        (
            "App Store Subscription State Report Standard",
            "Date\tApp Apple Identifier\tState Metric\tCounts",
            f"{DAY}\t123\tFull price\t7",
            "paid_subscriptions",
        ),
        (
            "App Store Subscription Event Report Standard",
            "Event Date\tApp Apple Identifier\tEvent Group\tEvent Name\tCounts",
            f"{DAY}\t123\tPaid subscription start\tFull price subscription start activation\t7",
            "paid_starts",
        ),
    ],
)
async def test_collect_matches_literal_report_names_returned_by_apple(report_name, columns, values, metric):
    """API 返回名称须直接驱动整条采集链，fixture 不从实现常量反推名称。"""

    async def transport(request):
        path = request.url.path
        if request.url.host.endswith("amazonaws.com"):
            raw = (columns + "\n" + values + "\n").encode()
            return httpx.Response(200, stream=httpx.ByteStream(gzip.compress(raw)))
        if path.endswith("/analyticsReportRequests"):
            item = {
                "id": "req",
                "type": "analyticsReportRequests",
                "attributes": {"accessType": "ONGOING", "stoppedDueToInactivity": False},
            }
        elif path.endswith("/reports"):
            item = {"id": "report", "type": "analyticsReports", "attributes": {"name": report_name}}
        elif path.endswith("/instances"):
            item = {
                "id": "instance",
                "type": "analyticsReportInstances",
                "attributes": {"granularity": "DAILY", "processingDate": "2026-10-21"},
            }
        elif path.endswith("/segments"):
            item = {"id": "segment", "type": "analyticsReportSegments", "attributes": {"url": DOWNLOAD}}
        else:
            raise AssertionError(path)
        return httpx.Response(200, json=collection([item]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        result = await AppleAnalyticsClient(config(), client=http).collect("123", DAY)
    assert result.metrics[metric].status == "available"
    assert result.metrics[metric].value == 7
    assert result.metrics[metric].source == report_name


def test_event_header_aliases_cannot_hide_duplicate_columns():
    from dwy_apple_notify.analytics.metrics import EVENTS

    raw = ("Event Date\tApp Apple Identifier\tEvent Group\tEvent Grouping\tEvent Sub Type\tCounts\n"
           f"{DAY}\t123\tPaid subscription start\tRenewals\tFull price subscription start activation\t7\n")
    with pytest.raises(AnalyticsCollectionError, match="^analytics_invalid_report$"):
        AppleAnalyticsClient._rows(raw.encode(), EVENTS)
