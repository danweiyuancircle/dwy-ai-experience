"""公开评分配置及 Lookup 外部输入边界。"""

import httpx
import pytest
from pydantic import ValidationError

from dwy_apple_notify.ratings import (
    AppleRating,
    AppleRatingClient,
    AppleRatingsConfig,
    RatingApp,
    RatingCollectionError,
)


def config(**changes):
    return AppleRatingsConfig(apps={"123": RatingApp(name="Demo")}, **changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"timezone": "Invalid/Zone"},
        {"send_hour": 24},
        {"send_minute": 60},
        {"retention_days": 31},
        {"territories": ()},
        {"territories": ("CN",)},
        {"territories": ("cn", "cn")},
        {"apps": {"abc": {"name": "Demo"}}},
    ],
)
def test_configuration_rejects_invalid_boundaries(changes):
    with pytest.raises(ValidationError):
        AppleRatingsConfig.model_validate({"apps": {"123": {"name": "Demo"}}, **changes})


def test_defaults_and_raw_precision():
    options = config()
    assert (options.timezone, options.send_hour, options.send_minute) == ("Asia/Shanghai", 8, 30)
    assert options.territories == ("cn", "us") and options.retention_days == 90
    assert AppleRating(count=3, average=4.6666666667).average == 4.6666666667
    assert AppleRating(count=0, average=0).average == 0


@pytest.mark.parametrize(
    "count,average",
    [(True, 4), (-1, 4), (1.0, 4), (0, 4), (1, 0), (1, 5.1), (1, float("nan")), (1, True), (2**63, 4)],
)
def test_rating_requires_consistent_aggregates(count, average):
    with pytest.raises(ValidationError):
        AppleRating(count=count, average=average)


async def test_lookup_uses_all_version_fields_and_configured_scope():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "resultCount": 1,
                "results": [
                    {
                        "trackId": 123,
                        "userRatingCount": 3,
                        "averageUserRating": 4.6666666667,
                        "userRatingCountForCurrentVersion": 999,
                        "averageUserRatingForCurrentVersion": 1,
                    }
                ],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        client = AppleRatingClient(config(), client=http)
        assert await client.get_rating("123", "cn") == AppleRating(count=3, average=4.6666666667)
        assert str(requests[0].url) == "https://itunes.apple.com/lookup?id=123&country=cn"
        with pytest.raises(RatingCollectionError, match="rating_unknown_scope"):
            await client.get_rating("456", "cn")
        with pytest.raises(RatingCollectionError, match="rating_unknown_scope"):
            await client.get_rating("123", "fr")
        await client.aclose()
        assert not http.is_closed


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"resultCount": 0, "results": []},
        {"resultCount": 1, "results": [{"trackId": 456, "userRatingCount": 1, "averageUserRating": 4}]},
        {"resultCount": 1, "results": [{"trackId": 123, "userRatingCount": 1}]},
        {"resultCount": 1, "results": [{"trackId": 123, "userRatingCount": 0, "averageUserRating": 4}]},
        {"resultCount": True, "results": [{"trackId": 123}]},
    ],
)
async def test_lookup_invalid_payload_never_returns_zero(payload):
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload),
        )
    ) as http:
        with pytest.raises(RatingCollectionError, match="rating_invalid_response"):
            await AppleRatingClient(config(), client=http).get_rating("123", "cn")


@pytest.mark.parametrize("status", [301, 404, 429, 500])
async def test_lookup_http_failures_are_safe_and_not_retried(status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, text="secret response", headers={"location": "https://example.com"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(RatingCollectionError, match="rating_http_error"):
            await AppleRatingClient(config(), client=http).get_rating("123", "cn")
    assert len(calls) == 1


async def test_lookup_timeout_malformed_and_oversized_response():
    def timeout(request):
        raise httpx.ReadTimeout("secret", request=request)

    for handler, code in [
        (timeout, "rating_request_error"),
        (lambda request: httpx.Response(200, text="not JSON"), "rating_invalid_response"),
        (lambda request: httpx.Response(200, content=b"x" * (1024 * 1024 + 1)), "rating_response_too_large"),
    ]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            with pytest.raises(RatingCollectionError, match=code):
                await AppleRatingClient(config(), client=http).get_rating("123", "cn")


async def test_lookup_deeply_nested_json_is_an_invalid_response():
    content = "[" * 2000 + "0" + "]" * 2000
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, content=content)),
    ) as http:
        with pytest.raises(RatingCollectionError, match="rating_invalid_response"):
            await AppleRatingClient(config(), client=http).get_rating("123", "cn")
