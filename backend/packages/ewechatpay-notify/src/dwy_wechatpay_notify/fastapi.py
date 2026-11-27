"""可选 FastAPI 入口；只负责接收事件，不管理宿主账本或通知队列。"""

from dwy_notify.events import EventSink
from fastapi import FastAPI, Request, Response

from .events import wechatpay_notification_event
from .models import WechatPayNotifyConfig
from .verifier import WechatPayNotificationVerifier, WechatPayVerificationError


def install_wechatpay_notifications(
    app: FastAPI, config: WechatPayNotifyConfig, *, verifier: WechatPayNotificationVerifier, sink: EventSink
) -> None:
    """显式持久 sink 成功或重复才确认；注入的 SDK/sink 生命周期由宿主管理。"""
    if not callable(sink):
        raise TypeError("an explicit EventSink is required")
    if verifier.config != config:
        raise ValueError("verifier and route configuration must match")
    if hasattr(app.state, "dwy_wechatpay_notify"):
        raise ValueError("Wechat Pay notifications already installed")
    if any(getattr(route, "path", None) == config.path for route in app.routes):
        raise ValueError("Wechat Pay callback path already registered")

    async def receive(request: Request) -> Response:
        chunks, size = [], 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > config.max_body_bytes:
                return Response(status_code=413)
            chunks.append(chunk)
        try:
            result = await verifier.verify(request.headers, b"".join(chunks))
        except WechatPayVerificationError:
            return Response(status_code=400)
        try:
            await sink(wechatpay_notification_event(result, scope=config.scope))
        except Exception:
            # 接收器失败必须让微信重试；正文不暴露宿主异常或敏感内容。
            return Response(status_code=503)
        return Response(status_code=204)

    app.add_api_route(config.path, receive, methods=["POST"], include_in_schema=False)
    app.state.dwy_wechatpay_notify = verifier
