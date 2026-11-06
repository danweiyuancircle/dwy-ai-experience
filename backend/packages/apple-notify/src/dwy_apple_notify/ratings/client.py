"""有界读取 Apple 公开 Lookup，不使用账号认证或当前版本评分字段。"""

import json

import httpx
from pydantic import ValidationError

from .models import AppleRating, AppleRatingsConfig, RatingCollectionError

_MAX_BYTES = 1024 * 1024


class AppleRatingClient:
    """自有 HTTP 客户端通过 aclose 释放；注入客户端由宿主负责关闭。"""

    def __init__(self, config: AppleRatingsConfig, *, client: httpx.AsyncClient | None = None):
        self.config = config
        self._owns_client = client is None
        self._client = (
            client
            if client is not None
            else httpx.AsyncClient(
                timeout=20,
                follow_redirects=False,
                trust_env=False,
            )
        )

    async def get_rating(self, app_id: str, territory: str) -> AppleRating:
        """每次只请求一个已配置地区，无 HTTP 重试；失败不返回空或零基线。"""
        if app_id not in self.config.apps or territory not in self.config.territories:
            raise RatingCollectionError("rating_unknown_scope")
        try:
            async with self._client.stream(
                "GET",
                "https://itunes.apple.com/lookup",
                params={"id": app_id, "country": territory},
                headers={"Accept": "application/json"},
                timeout=20,
                follow_redirects=False,
            ) as response:
                if response.status_code != 200:
                    raise RatingCollectionError("rating_http_error")
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    if len(content) + len(chunk) > _MAX_BYTES:
                        raise RatingCollectionError("rating_response_too_large")
                    content.extend(chunk)
        except httpx.HTTPError:
            raise RatingCollectionError("rating_request_error") from None
        try:
            payload = json.loads(content)
            if (
                not isinstance(payload, dict)
                or type(payload.get("resultCount")) is not int
                or payload["resultCount"] != 1
                or not isinstance(payload.get("results"), list)
                or len(payload["results"]) != 1
            ):
                raise ValueError
            item = payload["results"][0]
            if (
                not isinstance(item, dict)
                or type(item.get("trackId")) is not int
                or str(item["trackId"]) != app_id
            ):
                raise ValueError
            return AppleRating(count=item["userRatingCount"], average=item["averageUserRating"])
        except (KeyError, TypeError, ValueError, UnicodeError, ValidationError, RecursionError):
            raise RatingCollectionError("rating_invalid_response") from None

    async def aclose(self) -> None:
        """只关闭库自己创建的客户端，可重复调用。"""
        if self._owns_client:
            await self._client.aclose()
