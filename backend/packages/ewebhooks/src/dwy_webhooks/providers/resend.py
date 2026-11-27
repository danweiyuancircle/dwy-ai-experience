"""Resend 入站适配：官方 SDK 验签后只交付事件元数据，不读取邮件正文。"""

import resend
from fastapi import APIRouter, HTTPException, Request

from ..config import ResendWebhookConfig
from ..events import EventSink, WebhookEvent
from . import accept_event, read_payload

# 未显式选择的事件不进入发送链；新事件文案仅在此来源文件扩展。
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


def create_resend_router(config: ResendWebhookConfig, sink: EventSink) -> APIRouter:
    """独立项目只提供来源配置和接收接口，去重或持久化属于 sink。"""
    router = APIRouter()

    @router.post(config.path, include_in_schema=False)
    async def receive(request: Request):
        """先限制并验证原始载荷，再解析类型，最后确认下游接收结果。"""
        raw = await read_payload(request)
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
        prepared = WebhookEvent(
            source="resend", scope=config.scope, event_id=event_id, event_type=event_type,
            content=content, data={"email_id": email_id},
        )
        return await accept_event(sink, prepared)

    return router
