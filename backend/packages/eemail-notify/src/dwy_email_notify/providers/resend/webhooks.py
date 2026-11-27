"""Resend 入站事件：验签后仅转发安全元数据，不发信或拉取邮件正文。"""

import resend
from dwy_notify.delivery import NotificationDeliveryError
from dwy_notify.events import EventSink, NotificationEvent
from fastapi import APIRouter, HTTPException, Request

from ...config import ResendWebhookConfig

EVENT_LABELS = {
    "email.received": "收到新邮件",
    "email.sent": "邮件已发送",
    "email.delivered": "邮件已送达",
    "email.failed": "邮件发送失败",
    "email.bounced": "邮件退信",
    "email.complained": "邮件被标记为垃圾邮件",
    "email.delivery_delayed": "邮件投递延迟",
    "email.suppressed": "邮件被抑制发送",
    "email.opened": "邮件被打开",
    "email.clicked": "邮件链接被点击",
}


async def _read_payload(request: Request) -> bytes:
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > 65536:
            raise HTTPException(413, "Webhook payload is too large")
    return bytes(raw)


def create_resend_router(config: ResendWebhookConfig, sink: EventSink) -> APIRouter:
    """独立路由只交付已验签事件；sink 成功接收后才能向 Resend 确认。"""
    router = APIRouter()

    @router.post(config.path, include_in_schema=False, status_code=200, response_model=dict[str, bool])
    async def receive(request: Request):
        """签名覆盖原始字节，未知事件先筛选，正文和第三方异常不进入通知。"""
        raw = await _read_payload(request)
        event_id = request.headers.get("svix-id", "")
        if not event_id or len(event_id) > 256:
            raise HTTPException(401, "Invalid webhook signature")
        try:
            event = resend.Webhooks.verify({
                "payload": raw.decode("utf-8"),
                "headers": {
                    "id": event_id,
                    "timestamp": request.headers.get("svix-timestamp", ""),
                    "signature": request.headers.get("svix-signature", ""),
                },
                "webhook_secret": config.secret.get_secret_value(),
            })
        except (ValueError, UnicodeError):
            raise HTTPException(401, "Invalid webhook signature") from None
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise HTTPException(400, "Invalid webhook event")
        event_type = event["type"]
        selected = config.events if config.events is not None else EVENT_LABELS
        if event_type not in selected:
            return {"received": True, "ignored": True}
        data = event.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("email_id"), str):
            raise HTTPException(400, "Invalid email event")
        email_id = data["email_id"][:128]
        content = "\n".join([
            f"{config.name} · {EVENT_LABELS.get(event_type, event_type)}",
            f"事件：{event_type}", f"邮件编号：{email_id}", f"通知编号：{event_id}",
        ])
        prepared = NotificationEvent(
            source="resend", scope=config.scope, event_id=event_id, event_type=event_type,
            content=content, data={"email_id": email_id},
        )
        try:
            accepted = await sink(prepared)
        except NotificationDeliveryError as error:
            message = ("Invalid notification acknowledgement" if error.code == "discord_invalid_response"
                       else "Notification delivery failed")
            raise HTTPException(502, message) from None
        if not isinstance(accepted, bool):
            raise RuntimeError("Webhook sink must return an acceptance boolean")
        return {"received": True, "duplicate": not accepted}

    return router
