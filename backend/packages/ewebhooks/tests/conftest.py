"""模拟统一通知 HTTP 边界，回调来源仍使用真实 ASGI 与验签链路。"""

import httpx
import pytest
import requests


@pytest.fixture
def capture_notification_http(monkeypatch):
    """仅替换 dwy-notify 的单次传输，禁止测试向外部 IM 发消息。"""
    def install(handler):
        def post(url, **kwargs):
            request = httpx.Request(
                "POST", url, params=kwargs.get("params"), headers=kwargs.get("headers"),
                content=kwargs.get("data"), json=kwargs.get("json"),
            )
            timeout = kwargs.get("timeout", 10)
            request.extensions["timeout"] = {"read": timeout[-1] if isinstance(timeout, tuple) else timeout}
            response = handler(request)
            result = requests.Response()
            result.status_code = response.status_code
            result._content = response.content
            result.headers.update(response.headers)
            return result

        monkeypatch.setattr("dwy_notify._transport.post", post)

    return install
