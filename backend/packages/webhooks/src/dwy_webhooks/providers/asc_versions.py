"""按事件关联版本读取详情；不查询最新版本，也不采用响应中的最新审核状态。"""

import json
import time
from contextlib import nullcontext
from urllib.parse import quote

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .._asc import asc_private_key, asc_token
from ..config import AppStoreConnectAPIConfig
from ..errors import WebhookDeliveryError


class AppStoreVersionMetadata(BaseModel):
    """仅保留经过校验的平台和版本号，防止外部字段注入多行通知。"""

    model_config = ConfigDict(frozen=True, extra="ignore")
    platform: str = Field(pattern=r"^[A-Z][A-Z0-9_]{0,31}$")
    version_string: str = Field(alias="versionString", min_length=1, max_length=64,
                                pattern=r"^[A-Za-z0-9][A-Za-z0-9 ._+\-]*$")


class AppStoreVersionClient:
    """使用宿主显式凭据；每次查询自有客户端及时关闭，注入客户端不由库关闭。"""

    def __init__(self, config: AppStoreConnectAPIConfig, *, client: httpx.AsyncClient | None = None,
                 clock=time.time):
        """构造时检查账号私钥，不发请求、不读取宿主环境或其他功能的配置。"""
        self._config, self._client, self._clock = config, client, clock
        self._key = asc_private_key(config.private_key)

    async def lookup(self, app_id: str, version_id: str) -> AppStoreVersionMetadata:
        """只访问固定 Apple 域名，确认资源编号和所属 App 后才返回详情。"""
        try:
            token = asc_token(self._config, self._key, self._clock)
        except ValueError:
            raise WebhookDeliveryError("asc_version_credentials_error") from None
        context = (nullcontext(self._client) if self._client is not None else httpx.AsyncClient(
            timeout=10, follow_redirects=False, trust_env=False,
        ))
        url = "https://api.appstoreconnect.apple.com/v1/appStoreVersions/" + quote(version_id, safe="")
        try:
            async with context as client, client.stream(
                "GET", url,
                params={"fields[appStoreVersions]": "platform,versionString,app", "include": "app"},
                headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
                follow_redirects=False, timeout=10,
            ) as response:
                if response.status_code != 200:
                    raise WebhookDeliveryError("asc_version_http_error")
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    if len(content) + len(chunk) > 65536:
                        raise WebhookDeliveryError("asc_version_response_too_large")
                    content.extend(chunk)
        except httpx.HTTPError:
            raise WebhookDeliveryError("asc_version_request_error") from None
        try:
            resource = json.loads(content)["data"]
            application = resource["relationships"]["app"]["data"]
            if (resource["type"] != "appStoreVersions" or resource["id"] != version_id
                    or application["type"] != "apps" or application["id"] != app_id):
                raise ValueError
            return AppStoreVersionMetadata.model_validate(resource["attributes"])
        except (KeyError, TypeError, ValueError, UnicodeError, ValidationError):
            raise WebhookDeliveryError("asc_version_invalid_response") from None
