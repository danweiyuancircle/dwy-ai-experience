"""Bounded official Analytics Reports discovery and unsigned gzip TSV downloads."""

import csv
import gzip
import io
import json
import re
import time
import zlib
from collections.abc import Callable
from datetime import date
from urllib.parse import urljoin, urlsplit

import httpx

from .._asc import asc_private_key, asc_token
from .metrics import DISCOVERY, DOWNLOADS, EVENTS, PURCHASES, REPORT_NAMES, STATE, aggregate_reports
from .models import AnalyticsCollectionError, AppleAnalyticsConfig, AppleBusinessSnapshot

_ORIGIN = "https://api.appstoreconnect.apple.com"
_MAX_PAGE_BYTES = 2 * 1024 * 1024
_MAX_PAGES = 100
_MAX_DOWNLOAD_BYTES = 16 * 1024 * 1024
_MAX_TSV_BYTES = 64 * 1024 * 1024
_MAX_ROWS = 200000
_MAX_SEGMENTS = 256
_MAX_INSTANCES = 64
_MAX_COLLECTION_BYTES = 128 * 1024 * 1024
_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_REQUIRED = {
    DOWNLOADS: {"Download Type", "Counts", "Territory", "Source Type"},
    DISCOVERY: {"Event", "Page Type", "Counts"},
    PURCHASES: {"Purchases", "Sales in USD", "Proceeds in USD", "Territory"},
    STATE: {"State Metric", "State Metric Grouping", "Counts"},
    EVENTS: {"Event Grouping", "Event Sub Type", "Counts"},
}


class AppleAnalyticsClient:
    """Injected HTTP resources remain host-owned; collect never requests report creation."""

    def __init__(
        self,
        config: AppleAnalyticsConfig,
        *,
        client: httpx.AsyncClient | None = None,
        clock: Callable[[], float] = time.time,
    ):
        self._config, self._clock = config, clock
        self._owns_client = client is None
        try:
            self._key = asc_private_key(config.private_key)
        except ValueError:
            raise AnalyticsCollectionError("analytics_invalid_credentials") from None
        self._client = (
            client
            if client is not None
            else httpx.AsyncClient(timeout=20, follow_redirects=False, trust_env=False)
        )

    def _app(self, app_id: str) -> None:
        if app_id not in self._config.apps:
            raise AnalyticsCollectionError("analytics_unknown_app")

    @staticmethod
    def _id(item: dict) -> str:
        value = item.get("id")
        if not isinstance(value, str) or not _ID.fullmatch(value):
            raise AnalyticsCollectionError("analytics_invalid_response")
        return value

    @staticmethod
    def _next(value: object, path: str) -> str | None:
        if value is None:
            return None
        try:
            if not isinstance(value, str) or not 1 <= len(value) <= 4096 or any(ord(c) < 33 for c in value):
                raise ValueError
            url = urljoin(_ORIGIN + path, value)
            parts = urlsplit(url)
            if (
                parts.scheme != "https"
                or parts.netloc not in {"api.appstoreconnect.apple.com", "api.appstoreconnect.apple.com:443"}
                or parts.path != path
                or parts.fragment
                or "#" in value
            ):
                raise ValueError
            return url
        except (ValueError, TypeError):
            raise AnalyticsCollectionError("analytics_invalid_pagination") from None

    async def _request(self, method: str, url: str, body: dict | None = None) -> dict:
        try:
            token = asc_token(self._config, self._key, self._clock)
            async with self._client.stream(
                method,
                url,
                json=body,
                headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
                follow_redirects=False,
                timeout=20,
            ) as response:
                if response.status_code not in ({201} if method == "POST" else {200}):
                    raise AnalyticsCollectionError("analytics_http_error")
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    if len(content) + len(chunk) > _MAX_PAGE_BYTES:
                        raise AnalyticsCollectionError("analytics_response_too_large")
                    content.extend(chunk)
            payload = json.loads(content)
            if not isinstance(payload, dict) or "errors" in payload:
                raise ValueError
            return payload
        except AnalyticsCollectionError:
            raise
        except httpx.HTTPError:
            raise AnalyticsCollectionError("analytics_request_error") from None
        except (ValueError, TypeError, UnicodeError, RecursionError):
            raise AnalyticsCollectionError("analytics_invalid_response") from None

    async def _list(self, path: str, resource: str, query: str = "") -> list[dict]:
        url = _ORIGIN + path + "?limit=200" + query
        seen, ids, result = set(), set(), []
        expected = None
        while url:
            if url in seen or len(seen) >= _MAX_PAGES:
                raise AnalyticsCollectionError("analytics_invalid_pagination")
            seen.add(url)
            payload = await self._request("GET", url)
            try:
                items, links = payload["data"], payload["links"]
                if not isinstance(items, list) or len(items) > 200 or not isinstance(links, dict):
                    raise ValueError
                total = payload.get("meta", {}).get("paging", {}).get("total")
                if total is not None:
                    if type(total) is not int or total < 0 or expected is not None and total != expected:
                        raise ValueError
                    expected = total
                for item in items:
                    if (
                        not isinstance(item, dict)
                        or item.get("type") != resource
                        or not isinstance(item.get("attributes"), dict)
                    ):
                        raise ValueError
                    identity = self._id(item)
                    if identity in ids:
                        raise ValueError
                    ids.add(identity)
                    result.append(item)
                url = self._next(links.get("next"), path)
                if (
                    url
                    and not items
                    or expected is not None
                    and len(result) > expected
                    or url is None
                    and expected is not None
                    and len(result) != expected
                    or payload.get("meta", {}).get("paging", {}).get("nextCursor")
                    and not url
                ):
                    raise ValueError
            except (KeyError, TypeError, ValueError, AttributeError):
                raise AnalyticsCollectionError("analytics_invalid_response") from None
        return result

    async def _requests(self, app_id: str) -> list[dict]:
        self._app(app_id)
        items = await self._list(
            f"/v1/apps/{app_id}/analyticsReportRequests",
            "analyticsReportRequests",
            "&filter[accessType]=ONGOING",
        )
        return [
            item
            for item in items
            if item.get("attributes", {}).get("accessType") == "ONGOING"
            and item["attributes"].get("stoppedDueToInactivity") is False
        ]

    async def initialize(self, app_id: str) -> str:
        """Explicit privileged bootstrap, idempotent while an ONGOING request is active."""
        existing = await self._requests(app_id)
        if existing:
            return self._id(existing[0])
        payload = await self._request(
            "POST",
            _ORIGIN + "/v1/analyticsReportRequests",
            {
                "data": {
                    "type": "analyticsReportRequests",
                    "attributes": {"accessType": "ONGOING"},
                    "relationships": {"app": {"data": {"type": "apps", "id": app_id}}},
                }
            },
        )
        item = payload.get("data")
        if not isinstance(item, dict) or item.get("type") != "analyticsReportRequests":
            raise AnalyticsCollectionError("analytics_invalid_response")
        return self._id(item)

    async def _download(self, url: object) -> bytes:
        try:
            if not isinstance(url, str) or not 1 <= len(url) <= 16384 or any(ord(c) < 33 for c in url):
                raise ValueError
            parts = urlsplit(url)
            host = parts.hostname or ""
            apple = host.endswith((".apple.com", ".mzstatic.com"))
            s3 = re.fullmatch(r"asp-[a-z0-9-]+\.s3(?:\.[a-z0-9-]+)?\.amazonaws\.com", host)
            if (
                parts.scheme != "https"
                or not (apple or s3)
                or parts.username
                or parts.password
                or parts.port not in (None, 443)
                or parts.fragment
            ):
                raise ValueError
        except (ValueError, TypeError):
            raise AnalyticsCollectionError("analytics_invalid_download") from None
        try:
            # Build a fresh request to exclude an injected client's default bearer headers/cookies.
            request = httpx.Request("GET", url, headers={"Accept": "application/octet-stream"})
            response = await self._client.send(request, stream=True, follow_redirects=False, auth=None)
            try:
                if response.status_code != 200:
                    raise AnalyticsCollectionError("analytics_download_error")
                compressed = bytearray()
                async for chunk in response.aiter_raw():
                    if len(compressed) + len(chunk) > _MAX_DOWNLOAD_BYTES:
                        raise AnalyticsCollectionError("analytics_download_too_large")
                    compressed.extend(chunk)
            finally:
                await response.aclose()
            with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as zipped:
                raw = zipped.read(_MAX_TSV_BYTES + 1)
            if len(raw) > _MAX_TSV_BYTES:
                raise AnalyticsCollectionError("analytics_report_too_large")
            return raw
        except AnalyticsCollectionError:
            raise
        except (httpx.HTTPError, httpx.StreamError, OSError, EOFError, ValueError, zlib.error):
            raise AnalyticsCollectionError("analytics_download_error") from None

    @staticmethod
    def _rows(raw: bytes, source: str) -> list[dict[str, str]]:
        try:
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter="\t", strict=True)
            columns = reader.fieldnames
            required = _REQUIRED[source] | {
                "App Apple Identifier",
                "Event Date" if source == EVENTS else "Date",
            }
            if (
                not columns
                or len(columns) > 128
                or len(columns) != len(set(columns))
                or not required.issubset(columns)
            ):
                raise ValueError
            rows = []
            for row in reader:
                if (
                    len(rows) >= _MAX_ROWS
                    or None in row
                    or None in row.values()
                    or any(len(v) > 32768 or "\x00" in v for v in row.values())
                ):
                    raise ValueError
                rows.append(row)
            return rows
        except (UnicodeError, csv.Error, ValueError, TypeError):
            raise AnalyticsCollectionError("analytics_invalid_report") from None

    async def collect(self, app_id: str, report_date: date) -> AppleBusinessSnapshot:
        """Latest processing instance replaces each report date across all of its segments."""
        requests = await self._requests(app_id)
        if not requests:
            return aggregate_reports(
                app_id,
                report_date,
                {},
                pending=REPORT_NAMES,
                notes=("ONGOING report request is not active; initialize explicitly",),
            )
        reports, selected, pending = [], {}, []
        for item in requests:
            reports.extend(
                await self._list(f"/v1/analyticsReportRequests/{self._id(item)}/reports", "analyticsReports")
            )
        segment_count, collection_bytes = 0, 0
        for report in reports:
            source = report.get("attributes", {}).get("name")
            if source not in REPORT_NAMES:
                continue
            instances = await self._list(
                f"/v1/analyticsReports/{self._id(report)}/instances",
                "analyticsReportInstances",
                "&filter[granularity]=DAILY",
            )
            relevant = []
            try:
                for instance in instances:
                    attrs = instance["attributes"]
                    processing = date.fromisoformat(attrs["processingDate"])
                    if attrs["granularity"] == "DAILY" and processing >= report_date:
                        relevant.append((processing, self._id(instance)))
            except (KeyError, ValueError, TypeError):
                raise AnalyticsCollectionError("analytics_invalid_response") from None
            if len(relevant) > _MAX_INSTANCES:
                raise AnalyticsCollectionError("analytics_collection_limit")
            if not relevant:
                pending.append(source)
            for processing, identity in sorted(relevant):
                segments = await self._list(
                    f"/v1/analyticsReportInstances/{identity}/segments", "analyticsReportSegments"
                )
                segment_count += len(segments)
                if segment_count > _MAX_SEGMENTS:
                    raise AnalyticsCollectionError("analytics_collection_limit")
                rows = []
                for segment in segments:
                    raw = await self._download(segment.get("attributes", {}).get("url"))
                    collection_bytes += len(raw)
                    if collection_bytes > _MAX_COLLECTION_BYTES:
                        raise AnalyticsCollectionError("analytics_collection_limit")
                    rows.extend(self._rows(raw, source))
                    if len(rows) > _MAX_ROWS:
                        raise AnalyticsCollectionError("analytics_collection_limit")
                day_field = "Event Date" if source == EVENTS else "Date"
                matching = [r for r in rows if r[day_field] == report_date.isoformat()]
                if matching and (source not in selected or processing > selected[source][0]):
                    selected[source] = processing, matching
        data = {source: version[1] for source, version in selected.items()}
        return aggregate_reports(app_id, report_date, data, pending=tuple(pending))

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
