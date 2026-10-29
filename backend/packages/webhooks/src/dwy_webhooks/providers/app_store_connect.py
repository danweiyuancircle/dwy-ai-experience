"""App Store Connect 入站适配：按应用验原始字节 HMAC，不依赖宿主账本。"""

import hashlib
import hmac
import json
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from ..config import AppStoreConnectWebhookConfig
from ..errors import WebhookDeliveryError
from ..events import EventSink, WebhookEvent
from . import accept_event, read_payload

if TYPE_CHECKING:
    from .asc_versions import AppStoreVersionClient, AppStoreVersionMetadata

EVENTS = {
    "appStoreVersionAppVersionStateUpdated": ("版本审核状态", "appStoreVersions"),
    "buildUploadStateUpdated": ("构建上传状态", "buildUploads"),
}
STATES = {
    "PREPARE_FOR_SUBMISSION": "准备提交", "READY_FOR_REVIEW": "准备送审",
    "WAITING_FOR_REVIEW": "等待审核", "IN_REVIEW": "审核中",
    "WAITING_FOR_EXPORT_COMPLIANCE": "等待出口合规处理", "PENDING_CONTRACT": "等待协议处理",
    "REJECTED": "审核被拒", "METADATA_REJECTED": "元数据被拒",
    "DEVELOPER_REJECTED": "开发者撤回", "INVALID_BINARY": "构建无效",
    "PENDING_DEVELOPER_RELEASE": "审核通过，等待开发者发布",
    "PENDING_APPLE_RELEASE": "等待 Apple 发布", "PROCESSING_FOR_APP_STORE": "正在处理上架",
    "READY_FOR_SALE": "已上架", "READY_FOR_DISTRIBUTION": "可供分发",
    "REMOVED_FROM_SALE": "已下架", "DEVELOPER_REMOVED_FROM_SALE": "开发者已下架",
    "REPLACED_WITH_NEW_VERSION": "已被新版本替代", "ACCEPTED": "上传已接收",
    "PROCESSING": "上传处理中", "COMPLETE": "上传处理完成", "FAILED": "上传处理失败",
}


class EventAttributes(BaseModel):
    """两类状态通知字段不同；时间和原状态并非总是存在。"""

    newValue: str | None = Field(default=None, min_length=1, max_length=128)
    oldValue: str | None = Field(default=None, min_length=1, max_length=128)
    newState: str | None = Field(default=None, min_length=1, max_length=128)
    timestamp: datetime | None = None


class Resource(BaseModel):
    """外部 JSON:API 资源只取有界标识，不访问传入的 URL。"""

    type: str = Field(min_length=1, max_length=128)
    id: str = Field(min_length=1, max_length=128)


class Instance(BaseModel):
    """事件关联的版本或构建上传资源。"""

    data: Resource


class Relationships(BaseModel):
    """仅选择版本/构建状态事件后才要求 instance 关联。"""

    instance: Instance


class StatusEvent(Resource):
    """验证已选择的状态事件，不要求未选通知携带同一结构。"""

    version: int = Field(ge=1, le=100)
    attributes: EventAttributes
    relationships: Relationships


class Envelope(BaseModel):
    """先验证公共事件头，再判断是否为 ping 或已选择的状态类型。"""

    data: Resource


def message(app_id: str, name: str, event: StatusEvent,
            metadata: "AppStoreVersionMetadata | None" = None) -> str:
    """保留 Apple 原始状态；未知枚举可读，不猜测拒审原因或版本号。"""
    attrs = event.attributes
    state = attrs.newValue if event.type == "appStoreVersionAppVersionStateUpdated" else attrs.newState
    if state is None or event.relationships.instance.data.type != EVENTS[event.type][1]:
        raise ValueError("invalid status event")
    lines = [f"App Store Connect · {EVENTS[event.type][0]}", f"应用：{name}"]
    if event.type == "appStoreVersionAppVersionStateUpdated":
        if metadata is None:
            lines.extend(["平台：未查询（未配置 ASC API）", "版本：未查询（未配置 ASC API）"])
        else:
            platforms = {"IOS": "iOS", "MAC_OS": "macOS", "TV_OS": "tvOS", "VISION_OS": "visionOS"}
            lines.extend([f"平台：{platforms.get(metadata.platform, metadata.platform)}",
                          f"版本：{metadata.version_string}"])
    lines.append(f"状态：{STATES.get(state, state)} ({state})")
    if attrs.oldValue:
        lines.append(f"原状态：{STATES.get(attrs.oldValue, attrs.oldValue)} ({attrs.oldValue})")
    if attrs.timestamp:
        lines.append(f"事件时间：{attrs.timestamp.isoformat()}")
    lines.extend([f"记录编号：{event.relationships.instance.data.id}", f"通知编号：{event.id}",
                  f"后台：https://appstoreconnect.apple.com/apps/{app_id}/distribution"])
    return "\n".join(lines)


def create_asc_router(config: AppStoreConnectWebhookConfig, sink: EventSink, *,
                      version_client: "AppStoreVersionClient | None" = None) -> APIRouter:
    """按配置挂载应用独立密钥；接收语义由可替换的 sink 决定。"""
    router = APIRouter()
    if version_client is None and config.api is not None:
        from .asc_versions import AppStoreVersionClient

        version_client = AppStoreVersionClient(config.api)

    @router.post(config.path, include_in_schema=False)
    async def receive(app_id: str, request: Request):
        """签名覆盖原始字节；只在下游确认接收后向 Apple 返回成功。"""
        application = config.apps.get(app_id)
        if application is None:
            raise HTTPException(404, "Webhook is not configured")
        raw = await read_payload(request)
        digest = hmac.new(application.secret.get_secret_value().encode(), raw, hashlib.sha256).hexdigest()
        supplied = request.headers.get("x-apple-signature", "")
        if not supplied.isascii() or not hmac.compare_digest(supplied, "hmacsha256=" + digest):
            raise HTTPException(401, "Invalid webhook signature")
        try:
            envelope = Envelope.model_validate_json(raw)
            event_type, event_id = envelope.data.type, envelope.data.id
            selected = config.events if config.events is not None else {*EVENTS, "webhookPingCreated"}
            if event_type not in selected:
                return {"received": True, "ignored": True}
            if event_type == "webhookPingCreated":
                content = "\n".join([
                    "App Store Connect · 官方连通测试", f"应用：{application.name}",
                    "说明：验证 Apple → Cloud → Discord；不代表审核状态变化",
                    f"通知编号：{event_id}",
                    f"后台：https://appstoreconnect.apple.com/apps/{app_id}/distribution",
                ])
                data = {"app_id": app_id}
            elif event_type in EVENTS:
                event = StatusEvent.model_validate(json.loads(raw)["data"])
                state = (event.attributes.newValue if event_type == "appStoreVersionAppVersionStateUpdated"
                         else event.attributes.newState)
                if state is None or event.relationships.instance.data.type != EVENTS[event_type][1]:
                    raise ValueError("invalid status event")
                metadata = None
                if event_type == "appStoreVersionAppVersionStateUpdated" and version_client is not None:
                    metadata = await version_client.lookup(app_id, event.relationships.instance.data.id)
                content = message(app_id, application.name, event, metadata)
                data = {"app_id": app_id, "instance_id": event.relationships.instance.data.id, "state": state}
                if metadata is not None:
                    data.update(platform=metadata.platform, version_string=metadata.version_string)
            else:
                # 已配置但尚无适配器的类型仍明确忽略，不伪造可处理事件。
                return {"received": True, "ignored": True}
        except WebhookDeliveryError:
            # 不确认缺少详情的完整通知，让 Apple 重投；不泄露账号或响应内容。
            raise HTTPException(502, "Unable to read App Store version") from None
        except (ValidationError, ValueError, UnicodeError):
            raise HTTPException(400, "Invalid webhook event") from None
        prepared = WebhookEvent(
            source="app_store_connect", scope=app_id, event_id=event_id, event_type=event_type,
            content=content, data=data,
        )
        return await accept_event(sink, prepared)

    return router
