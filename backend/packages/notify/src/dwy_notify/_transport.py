"""Discord / 企业微信的单次 HTTP 边界，便于宿主测试替换。"""

import math
from typing import Any

import requests


def post(url: str, **kwargs: Any) -> requests.Response:
    """执行一次 HTTP POST；安全参数由包内适配器显式传入。"""
    return requests.post(url, **kwargs)


def retry_after(response: requests.Response) -> float | None:
    try:
        value = response.json().get("retry_after", response.headers.get("Retry-After"))
    except (ValueError, AttributeError):
        value = response.headers.get("Retry-After")
    if isinstance(value, bool):
        return None
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if math.isfinite(seconds) and seconds >= 0 else None


def send(plugin: Any, url: str, payload: dict, *, params: dict | None = None) -> requests.Response | None:
    try:
        response = post(
            url,
            json=payload,
            params=params,
            headers={"User-Agent": plugin.app_id},
            verify=True,
            timeout=plugin.socket_read_timeout,
            allow_redirects=False,
        )
    except requests.Timeout:
        plugin.outcome = {"error_code": "timeout"}
        return None
    except requests.RequestException:
        plugin.outcome = {"error_code": "network_error"}
        return None

    if response.status_code == 429:
        plugin.outcome = {"error_code": "rate_limited", "retry_after": retry_after(response)}
        return None
    if 300 <= response.status_code < 400:
        plugin.outcome = {"error_code": "redirect_rejected", "permanent": True}
        return None
    if not 200 <= response.status_code < 300:
        plugin.outcome = {
            "error_code": "http_error",
            "permanent": 400 <= response.status_code < 500 and response.status_code != 408,
        }
        return None
    return response
