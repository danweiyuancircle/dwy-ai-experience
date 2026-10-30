"""Apple 评论采集仅访问官方 API，完整分页成功后才返回数据。"""

import json

import httpx
import jwt
import pytest
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from pydantic import ValidationError

from dwy_apple_notify.reviews.client import AppleReviewClient
from dwy_apple_notify.reviews.models import (
    AppleReview,
    AppleReviewsConfig,
    ReviewApp,
    ReviewCollectionError,
)

APP_ID = "6777080682"
BASE = f"https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/customerReviews"
ISSUER = "01234567-89ab-cdef-0123-456789abcdef"


@pytest.fixture
def signing_key():
    """现场生成测试密钥，验签不依赖被测客户端自身实现。"""
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture
def config(signing_key):
    """调用方显式注入全部配置，不依赖环境。"""
    pem = signing_key.private_bytes(serialization.Encoding.PEM,
                                   serialization.PrivateFormat.PKCS8,
                                   serialization.NoEncryption()).decode()
    return AppleReviewsConfig(apps={APP_ID: ReviewApp(name="Test App")},
                              issuer_id=ISSUER, key_id="AB12345678", private_key=pem)


def resource(review_id="review-1", **attributes):
    """保留 Apple JSON:API 字段名以验证领域模型转换。"""
    return {"type": "customerReviews", "id": review_id, "attributes": {
        "rating": 5, "title": "Useful", "body": "Works well", "reviewerNickname": "Reader",
        "createdDate": "2026-10-25T13:00:00Z", "territory": "USA", **attributes,
    }}


def page(*reviews, next_url=None, total=None):
    """构建官方分页响应，不通过客户端编码器自证解析。"""
    value = {"data": list(reviews), "links": {"self": BASE, "next": next_url}}
    if total is not None:
        value["meta"] = {"paging": {"total": total, "limit": 200}}
    return value


@pytest.mark.asyncio
async def test_authenticated_pages_map_reviews_and_keep_injected_client(config, signing_key):
    """短期 ES256 token 可独立验签；分页去重，外部客户端仍由宿主关闭。"""
    requests = []

    def respond(request):
        requests.append(request)
        payload = page(resource(), next_url=BASE + "?cursor=2", total=2) if len(requests) == 1 else page(
            resource(), resource("review-2", rating=2), total=2)
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        client = AppleReviewClient(config, client=http, clock=lambda: 1_800_000_000)
        reviews = await client.list_reviews(APP_ID)
        await client.aclose()
        assert not http.is_closed
    assert [review.id for review in reviews] == ["review-1", "review-2"]
    assert reviews[0].reviewer_nickname == "Reader"
    assert reviews[0].created_at.utcoffset().total_seconds() == 0
    assert requests[0].url.params["sort"] == "-createdDate"
    assert requests[0].url.params["limit"] == "200"
    assert all(str(request.url).startswith(BASE) for request in requests)
    token = requests[0].headers["authorization"].removeprefix("Bearer ")
    claims = jwt.decode(token, signing_key.public_key(), algorithms=["ES256"],
                        audience="appstoreconnect-v1", options={"verify_exp": False,
                                                                "verify_iat": False})
    assert claims == {"iss": ISSUER, "iat": 1_800_000_000, "exp": 1_800_000_300,
                      "aud": "appstoreconnect-v1"}
    assert jwt.get_unverified_header(token) == {"alg": "ES256", "kid": "AB12345678", "typ": "JWT"}


@pytest.mark.parametrize("field,value", [
    ("apps", {}), ("apps", {"bad/id": {"name": "Bad"}}), ("poll_interval_seconds", 59),
    ("poll_interval_seconds", 604801), ("retention_days", 0), ("retention_days", 3651),
    ("issuer_id", "bad issuer"), ("key_id", "invalid"),
    ("discord_webhook_url", "https://evil.invalid/private-token"),
])
def test_configuration_rejects_invalid_boundaries(config, field, value):
    """配置错误在启动时暴露，不等待后台任务悄悄失败。"""
    with pytest.raises(ValidationError):
        AppleReviewsConfig(**{**config.model_dump(), field: value})


def test_defaults_do_not_read_environment_and_secret_repr_is_hidden(config, monkeypatch):
    """库只消费显式参数，密钥不得进入 repr。"""
    monkeypatch.setenv("APPLE_REVIEWS_RETENTION_DAYS", "999")
    assert config.retention_days == 30 and config.poll_interval_seconds == 3600
    assert "PRIVATE KEY" not in repr(config)
    assert "private_key" not in repr(config)
    with pytest.raises(ValidationError):
        config.retention_days = 60


@pytest.mark.parametrize("attributes", [
    {"rating": 0}, {"rating": 6}, {"rating": True}, {"title": "x" * 1001},
    {"body": "x" * 20001}, {"reviewerNickname": "x" * 257},
    {"createdDate": "2026-10-25T13:00:00"}, {"territory": "bad"},
])
@pytest.mark.asyncio
async def test_malformed_review_never_becomes_empty_success(config, attributes):
    """越界和无时区日期必须阻止整次同步。"""
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=page(resource(**attributes))),
    )) as http:
        with pytest.raises(ReviewCollectionError) as error:
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert error.value.code == "review_invalid_response"
    assert "Works well" not in str(error.value)


@pytest.mark.parametrize("next_url", [
    "https://evil.invalid/steal", "http://api.appstoreconnect.apple.com/v1/apps/6777080682/customerReviews",
    "https://api.appstoreconnect.apple.com:444/v1/apps/6777080682/customerReviews",
    "https://user:secret@api.appstoreconnect.apple.com/v1/apps/6777080682/customerReviews",
    "https://api.appstoreconnect.apple.com/v1/apps/1/customerReviews",
    "https://api.appstoreconnect.apple.com/v1/apps/6777080682/customerReviews/responses",
    BASE + "#fragment", "//evil.invalid/steal", "", 123, {"href": BASE},
])
@pytest.mark.asyncio
async def test_untrusted_pagination_is_rejected_before_following(config, next_url):
    """分页不能携带凭据跨域，也不能静默截断。"""
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json=page(resource(), next_url=next_url))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True) as http:
        with pytest.raises(ReviewCollectionError) as error:
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert error.value.code == "review_invalid_pagination"
    assert len(requests) == 1


@pytest.mark.parametrize("payload", [
    {}, {"data": []}, {"data": [], "links": []}, {"data": [], "links": {}},
    {"data": {}, "links": {"next": None}},
    page(total=1), page(resource(), total=2),
    {"data": [], "links": {"next": BASE + "?cursor=2"}},
])
@pytest.mark.asyncio
async def test_missing_or_truncated_collection_is_an_error(config, payload):
    """缺页与声明总数不一致都不能建立基线。"""
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload),
    )) as http:
        with pytest.raises(ReviewCollectionError):
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", [
    httpx.Response(403, text="sensitive upstream body"),
    httpx.Response(302, headers={"location": "https://evil.invalid/"}),
    httpx.Response(200, text="sensitive invalid json"),
    httpx.ConnectError("sensitive connection detail"),
])
async def test_errors_and_redirects_are_sanitized(config, outcome):
    """请求错误、HTTP 错误和非法 JSON 不回显正文、token 或原异常。"""
    requests = []

    def respond(request):
        requests.append(request)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True) as http:
        with pytest.raises(ReviewCollectionError) as error:
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert "sensitive" not in str(error.value)
    assert error.value.__suppress_context__ is True
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_response_byte_limit_applies_without_honest_content_length(config):
    """按实际读取字节限额，不能相信远端 Content-Length。"""
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, content=b" " * (2 * 1024 * 1024 + 1), headers={"content-length": "1"},
    ))) as http:
        with pytest.raises(ReviewCollectionError) as error:
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert error.value.code == "review_response_too_large"


@pytest.mark.asyncio
async def test_pagination_cycle_fails_instead_of_returning_partial_data(config):
    """循环游标会使上层永远无法取得完整快照。"""
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json=page(resource(), next_url=BASE + "?cursor=loop"),
    ))) as http:
        with pytest.raises(ReviewCollectionError) as error:
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert error.value.code == "review_invalid_pagination"


@pytest.mark.asyncio
async def test_page_cap_fails_instead_of_truncating(config):
    """固定页数上限让恶意无限游标不能占用无限资源。"""
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json=page(resource(str(len(requests))),
                                           next_url=BASE + f"?cursor={len(requests)}"))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        with pytest.raises(ReviewCollectionError) as error:
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert error.value.code == "review_collection_limit"
    assert len(requests) == 100


@pytest.mark.asyncio
async def test_unknown_app_cannot_change_the_request_path(config):
    """公开方法仅允许显式配置的 App ID。"""
    requests = []
    transport = httpx.MockTransport(lambda request: requests.append(request))
    async with httpx.AsyncClient(transport=transport) as http:
        with pytest.raises(ReviewCollectionError):
            await AppleReviewClient(config, client=http).list_reviews("../steal")
    assert not requests


@pytest.mark.asyncio
async def test_invalid_pem_has_safe_error(config):
    """私钥解析错误不泄漏原始 PEM 或底层异常。"""
    bad = config.model_copy(update={"private_key": "sensitive invalid PEM"})
    with pytest.raises(ReviewCollectionError) as error:
        client = AppleReviewClient(bad)
        try:
            await client.list_reviews(APP_ID)
        finally:
            await client.aclose()
    assert error.value.code == "review_invalid_credentials"
    assert "sensitive" not in str(error.value)


@pytest.mark.asyncio
async def test_owned_client_is_closed_and_does_not_trust_host_proxy_environment(config, monkeypatch):
    """宿主代理环境不能改变默认采集目的地，自建资源必须释放。"""
    http = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=page()),
    ))
    options = []

    def factory(**kwargs):
        options.append(kwargs)
        return http

    monkeypatch.setattr("dwy_apple_notify.reviews.client.httpx.AsyncClient", factory)
    client = AppleReviewClient(config)
    assert await client.list_reviews(APP_ID) == []
    await client.aclose()
    await client.aclose()
    assert http.is_closed
    assert options == [{"timeout": 20, "follow_redirects": False, "trust_env": False}]


@pytest.mark.parametrize("payload", [
    {"data": [], "links": {"self": BASE}, "meta": None},
    {"data": [], "links": {"self": BASE}, "meta": {"paging": {"total": True}}},
    {"data": [], "links": {"self": BASE}, "meta": {"paging": {"total": -1}}},
    {"data": [], "links": {"self": BASE}, "meta": {"paging": {"limit": 200, "nextCursor": "2"}}},
    page(*[resource(str(index)) for index in range(201)]),
])
@pytest.mark.asyncio
async def test_metadata_and_page_size_cannot_hide_truncation(config, payload):
    """声明下一游标却没有链接、负总数和越界页均不能提交成功。"""
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload),
    )) as http:
        with pytest.raises(ReviewCollectionError):
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [0, 200])
@pytest.mark.parametrize("include_meta", [False, True])
async def test_official_final_page_allows_optional_total_and_next(config, count, include_meta):
    """Apple total 与 next 都可缺省，恰好满页也可以是末页。"""
    payload = {"data": [resource(str(index)) for index in range(count)], "links": {"self": BASE}}
    if include_meta:
        payload["meta"] = {"paging": {"limit": 200}}
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload),
    )) as http:
        result = await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert len(result) == count


@pytest.mark.parametrize("next_url", [
    f"/v1/apps/{APP_ID}/customerReviews?cursor=2", "?cursor=2",
    f"//api.appstoreconnect.apple.com/v1/apps/{APP_ID}/customerReviews?cursor=2",
])
@pytest.mark.asyncio
async def test_official_uri_reference_next_is_resolved_to_same_origin(config, next_url):
    """官方 next 是 URI reference；相对链接仍须限定官方域名和当前应用路径。"""
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json=page(resource(), next_url=next_url) if len(requests) == 1
                              else page(resource("two")))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        result = await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert [review.id for review in result] == ["review-1", "two"]
    assert str(requests[1].url) == BASE + "?cursor=2"


@pytest.mark.asyncio
async def test_non_p256_private_key_is_rejected(config):
    """ES256 不能接受其他曲线，即使它们可以加载为 EC PEM。"""
    key = ec.generate_private_key(ec.SECP384R1())
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    bad = AppleReviewsConfig(**{**config.model_dump(), "private_key": pem})
    with pytest.raises(ReviewCollectionError) as error:
        AppleReviewClient(bad)
    assert error.value.code == "review_invalid_credentials"


def test_unsupported_private_key_algorithm_is_sanitized(config, monkeypatch):
    """底层密码库不支持的密钥格式同样只暴露稳定错误码。"""
    def load(*args, **kwargs):
        raise UnsupportedAlgorithm("sensitive provider details")

    monkeypatch.setattr("dwy_apple_notify.reviews.client.serialization.load_pem_private_key", load)
    with pytest.raises(ReviewCollectionError) as error:
        AppleReviewClient(config)
    assert error.value.code == "review_invalid_credentials"
    assert "sensitive" not in str(error.value)


def test_review_is_frozen_and_has_explicit_domain_fields():
    """持久化层获得稳定的领域字段，不需要理解 Apple 外部命名。"""
    review = AppleReview(id="one", rating=1, title="Title", body="Body",
                         reviewer_nickname="Reader", created_at="2026-10-25T13:00:00Z",
                         territory="USA")
    with pytest.raises(ValidationError):
        review.rating = 5


def test_review_id_matches_database_column_bound():
    """模型允许的外部 ID 不得超过持久化列长度。"""
    with pytest.raises(ValidationError):
        AppleReview(id="x" * 129, rating=1, title="Title", body="Body", reviewer_nickname="Reader",
                    created_at="2026-10-25T13:00:00Z", territory="USA")


@pytest.mark.parametrize("field", ["title", "body", "reviewerNickname"])
@pytest.mark.asyncio
async def test_invalid_unicode_is_rejected_before_formatting_or_persistence(config, field):
    """JSON 转义可以携带孤立代理点，必须先拒绝才能避免编码阶段反复失败。"""
    content = json.dumps(page(resource(**{field: "\ud800"}))).encode()
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=content),
    )) as http:
        with pytest.raises(ReviewCollectionError) as error:
            await AppleReviewClient(config, client=http).list_reviews(APP_ID)
    assert error.value.code == "review_invalid_response"
