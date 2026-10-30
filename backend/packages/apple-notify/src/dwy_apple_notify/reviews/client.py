"""有界读取官方 Customer Reviews API；整次分页完成后才交付快照。"""

import json
import time
from collections.abc import Callable
from urllib.parse import urljoin, urlsplit

import httpx
from pydantic import ValidationError

from .._asc import asc_private_key, asc_token
from .._asc import serialization as serialization
from .models import AppleReview, AppleReviewsConfig, ReviewCollectionError

_ORIGIN = "https://api.appstoreconnect.apple.com"
_MAX_PAGE_BYTES = 2 * 1024 * 1024
_MAX_PAGES = 100
_PAGE_SIZE = 200


class AppleReviewClient:
    """注入客户端由宿主关闭；自建客户端通过 aclose 释放，不跟随重定向。"""

    def __init__(self, config: AppleReviewsConfig, *, client: httpx.AsyncClient | None = None,
                 clock: Callable[[], float] = time.time):
        self._config = config
        self._clock = clock
        self._owns_client = client is None
        try:
            self._key = asc_private_key(config.private_key)
        except ValueError:
            raise ReviewCollectionError("review_invalid_credentials") from None
        self._client = client if client is not None else httpx.AsyncClient(
            timeout=20, follow_redirects=False, trust_env=False,
        )

    def _token(self) -> str:
        try:
            return asc_token(self._config, self._key, self._clock)
        except ValueError:
            raise ReviewCollectionError("review_invalid_credentials") from None

    @staticmethod
    def _next_url(value: object, path: str) -> str | None:
        if value is None:
            return None
        try:
            if not isinstance(value, str) or not value or len(value) > 2048:
                raise ValueError
            if any(ord(character) < 33 for character in value):
                raise ValueError
            resolved = urljoin(_ORIGIN + path, value)
            parts = urlsplit(resolved)
            if (parts.scheme != "https" or
                    parts.netloc not in {"api.appstoreconnect.apple.com", "api.appstoreconnect.apple.com:443"}
                    or parts.path != path or parts.fragment or "#" in value):
                raise ValueError
            return resolved
        except (ValueError, TypeError):
            raise ReviewCollectionError("review_invalid_pagination") from None

    async def _page(self, url: str) -> object:
        try:
            async with self._client.stream("GET", url, headers={
                "Authorization": "Bearer " + self._token(), "Accept": "application/json",
            }, follow_redirects=False, timeout=20) as response:
                if response.status_code != 200:
                    raise ReviewCollectionError("review_http_error") from None
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    if len(content) + len(chunk) > _MAX_PAGE_BYTES:
                        raise ReviewCollectionError("review_response_too_large") from None
                    content.extend(chunk)
        except httpx.HTTPError:
            raise ReviewCollectionError("review_request_error") from None
        try:
            return json.loads(content)
        except (ValueError, UnicodeError):
            raise ReviewCollectionError("review_invalid_response") from None

    @staticmethod
    def _parse_page(payload: object) -> tuple[list[AppleReview], object, int | None]:
        try:
            if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
                raise ValueError
            data = payload["data"]
            if len(data) > _PAGE_SIZE or not isinstance(payload.get("links"), dict):
                raise ValueError
            self_link = payload["links"].get("self")
            if not isinstance(self_link, str) or not 1 <= len(self_link) <= 2048:
                raise ValueError
            reviews = []
            for item in data:
                if not isinstance(item, dict) or item.get("type") != "customerReviews":
                    raise ValueError
                attributes = item["attributes"]
                reviews.append(AppleReview(
                    id=item["id"], rating=attributes["rating"], title=attributes["title"],
                    body=attributes["body"], reviewer_nickname=attributes["reviewerNickname"],
                    created_at=attributes["createdDate"], territory=attributes["territory"],
                ))
            total = None
            if "meta" in payload:
                paging = payload["meta"]["paging"]
                if not isinstance(paging, dict):
                    raise ValueError
                if "total" in paging:
                    total = paging["total"]
                    if type(total) is not int or total < 0:
                        raise ValueError
                if paging.get("nextCursor") is not None and payload["links"].get("next") is None:
                    raise ValueError
            return reviews, payload["links"].get("next"), total
        except (KeyError, ValueError, TypeError, ValidationError):
            raise ReviewCollectionError("review_invalid_response") from None

    async def list_reviews(self, app_id: str) -> list[AppleReview]:
        """完整读取已配置应用；任一页失败或超过限额均不返回部分评论。"""
        if app_id not in self._config.apps:
            raise ReviewCollectionError("review_unknown_app") from None
        path = f"/v1/apps/{app_id}/customerReviews"
        url: str | None = f"{_ORIGIN}{path}?sort=-createdDate&limit={_PAGE_SIZE}"
        visited = set()
        reviews: dict[str, AppleReview] = {}
        expected_total = None
        while url is not None:
            if url in visited:
                raise ReviewCollectionError("review_invalid_pagination") from None
            if len(visited) >= _MAX_PAGES:
                raise ReviewCollectionError("review_collection_limit") from None
            visited.add(url)
            page, next_value, total = self._parse_page(await self._page(url))
            if total is not None:
                if expected_total is not None and expected_total != total:
                    raise ReviewCollectionError("review_invalid_pagination") from None
                expected_total = total
            for review in page:
                reviews.setdefault(review.id, review)
            url = self._next_url(next_value, path)
            if (url is not None and not page or
                    expected_total is not None and len(reviews) > expected_total):
                raise ReviewCollectionError("review_invalid_pagination") from None
            # 官方 total 与 next 都是可选项；只在总数存在时核对完整性。
            if url is None and expected_total is not None and len(reviews) != expected_total:
                raise ReviewCollectionError("review_invalid_pagination") from None
        return list(reviews.values())

    async def aclose(self) -> None:
        """只释放库创建的 HTTP 客户端，可重复调用。"""
        if self._owns_client:
            await self._client.aclose()
