"""在仅安装 asc extra 的独立环境验证版本查询与审核通知。"""

import asyncio
import importlib.metadata
import importlib.util
import sys
from pathlib import Path

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

import dwy_apple_notify
from dwy_apple_notify.config import AppStoreConnectAPIConfig
from dwy_apple_notify.providers.app_store_connect import StatusEvent, message
from dwy_apple_notify.providers.asc_versions import AppStoreVersionClient


async def main(expected_version: str) -> None:
    """网络始终模拟；确认实际 wheel 的独立依赖、版本详情和事件状态契约。"""
    assert importlib.metadata.version("dwy-apple-notify") == expected_version
    assert Path(dwy_apple_notify.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    for name in ("app_cloud", "resend", "appstoreserverlibrary", "discord_webhook"):
        assert importlib.util.find_spec(name) is None, name
    key = ec.generate_private_key(ec.SECP256R1())
    config = AppStoreConnectAPIConfig(
        issuer_id="11111111-1111-1111-1111-111111111111", key_id="ABCDEFGHIJ",
        private_key=key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                      serialization.NoEncryption()).decode(),
    )

    def receive(request):
        assert request.url.path == "/v1/appStoreVersions/version-1"
        assert request.url.params["include"] == "app"
        return httpx.Response(200, json={"data": {
            "type": "appStoreVersions", "id": "version-1",
            "attributes": {"platform": "MAC_OS", "versionString": "2.3.1"},
            "relationships": {"app": {"data": {"type": "apps", "id": "123"}}},
        }})

    async with httpx.AsyncClient(transport=httpx.MockTransport(receive)) as http:
        metadata = await AppStoreVersionClient(config, client=http).lookup("123", "version-1")
        assert not http.is_closed
    event = StatusEvent.model_validate({
        "type": "appStoreVersionAppVersionStateUpdated", "id": "event-1", "version": 1,
        "attributes": {"newValue": "READY_FOR_DISTRIBUTION", "oldValue": "IN_REVIEW"},
        "relationships": {"instance": {"data": {"type": "appStoreVersions", "id": "version-1"}}},
    })
    content = message("123", "Wheel Test", event, metadata)
    assert "平台：macOS" in content and "版本：2.3.1" in content
    assert "状态：可供分发 (READY_FOR_DISTRIBUTION)" in content
    print(f"ASC wheel {expected_version}: isolated dependencies and review platform/version passed")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
