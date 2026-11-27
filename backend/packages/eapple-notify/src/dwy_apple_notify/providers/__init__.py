"""来源适配器共用的 HTTP 边界，不导入宿主、数据库或其他来源模块。"""

from dwy_notify.delivery import NotificationDeliveryError as WebhookDeliveryError
from dwy_notify.events import EventSink
from dwy_notify.events import NotificationEvent as WebhookEvent
from fastapi import HTTPException, Request


async def read_payload(request: Request, max_bytes: int = 65536) -> bytes:
    """读取期间限制实际字节，不信任可省略或伪造的 Content-Length。"""
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > max_bytes:
            raise HTTPException(413, "Webhook payload is too large")
    return bytes(raw)


async def accept_event(sink: EventSink, event: WebhookEvent) -> dict[str, bool]:
    """只有接收/转发成功才确认；失败不得写成成功去重或吞掉上游重试。"""
    try:
        accepted = await sink(event)
    except WebhookDeliveryError as error:
        message = ("Invalid notification acknowledgement" if error.code == "discord_invalid_response"
                   else "Notification delivery failed")
        raise HTTPException(502, message) from None
    if not isinstance(accepted, bool):
        raise RuntimeError("Webhook sink must return an acceptance boolean")
    return {"received": True, "duplicate": not accepted}
