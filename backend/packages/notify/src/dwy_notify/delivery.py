"""公共投递预算、逐目标恢复与安全失败状态；持久化和租约归宿主所有。"""

from __future__ import annotations

import math
import re
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from dwyeapi.exceptions import AppError
from pydantic import BaseModel, ConfigDict, Field

from .models import NotificationAppearance

if TYPE_CHECKING:
    from .notifier import Notifier


class NotificationDeliveryError(AppError):
    """发送失败；是否重试及如何持久化由调用方决定。"""

    def __init__(self, code: str, *, retry_after: float | None = None, permanent: bool = False):
        """retry_after 为有限非负秒数；生产发送器只使用固定错误码。"""
        self.code, self.retry_after, self.permanent = code, retry_after, permanent
        super().__init__(code, code=code)


class DeliveryPolicy(BaseModel):
    """调用方可显式注入投递预算，缺省与已有 ASC 消费者行为一致。"""

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_attempts: int = Field(default=8, ge=1, le=100)
    batch_size: int = Field(default=25, ge=1, le=500)
    lease_seconds: int = Field(default=60, ge=1, le=3600)
    poll_seconds: float = Field(default=2, gt=0, le=3600, allow_inf_nan=False)
    retry_cap_seconds: int = Field(default=3600, ge=1, le=86400)
    provider_retry_cap_seconds: int = Field(default=86400, ge=1, le=604800)


def delivery_failure(
    attempts: int, failure: NotificationDeliveryError, *, policy: DeliveryPolicy, clock: Callable[[], float],
) -> dict:
    """返回有界失败状态；只保留固定错误码，由调用方负责持久化。"""
    # 不持久化第三方发送器可能抛出的地址或响应正文。
    code = (failure.code if isinstance(failure.code, str)
            and re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", failure.code) else "webhook_delivery_error")
    delay = 0
    if (not isinstance(failure.retry_after, bool) and isinstance(failure.retry_after, (int, float))
            and math.isfinite(failure.retry_after) and failure.retry_after >= 0):
        delay = min(math.ceil(failure.retry_after), policy.provider_retry_cap_seconds)
    attempts += 1
    return dict(
        status="dead" if failure.permanent or attempts >= policy.max_attempts else "retry",
        attempts=attempts,
        next_attempt_at=int(clock()) + max(delay, min(policy.retry_cap_seconds, 2 ** attempts)),
        error_code=code,
    )


async def deliver_notifications(
    notifier: Notifier, payload: dict, *, policy: DeliveryPolicy, clock: Callable[[], float],
    checkpoint: Callable[..., Awaitable[bool]],
    appearance: NotificationAppearance | None = None,
) -> dict:
    """投递 payload['content'] 并返回聚合状态，不创建数据库或自行领取租约。

    checkpoint(**values) 必须按当前租约原子提交 payload 或 lease_until，成功才返回 True。
    返回 False 时立即停止并返回 processing；调用方不得把它标记成功或清除新租约。
    payload 必须是当前记录独立解码的可变字典，既有 notifications 状态会原地推进。
    每个成功目标后提交检查点；取消和检查点异常直接传播，网络确认丢失仍可能重复。
    """
    changed = False
    if appearance is not None and "appearance" not in payload:
        payload = dict(payload, appearance=appearance.model_dump(exclude_unset=True))
        changed = True
    if "notifications" not in payload:
        payload = dict(payload, notifications={
            name: dict(fingerprint=notifier.target_fingerprint(name), status="pending", attempts=0,
                       next_attempt_at=0, error_code=None, message_id=None)
            for name in notifier.targets
        })
        changed = True
    if changed:
        # 接收方与模块展示一并持久化；重启后不随新版默认预设变化。
        if not await checkpoint(payload=payload):
            return dict(status="processing")
    states = payload["notifications"]
    for name, state in states.items():
        if state["status"] in ("sent", "dead"):
            continue
        if name not in notifier.targets:
            state.update(status="dead", error_code="notification_target_missing")
        elif notifier.target_fingerprint(name) != state["fingerprint"]:
            state.update(status="dead", error_code="notification_target_changed")
        elif state["next_attempt_at"] <= int(clock()):
            # 每次网络前按 token 续租；批量目标不能沿用最初的租约到期时间。
            if not await checkpoint(lease_until=int(clock()) + policy.lease_seconds):
                return dict(status="processing")
            try:
                options = {}
                if "appearance" in payload:
                    options["default_appearance"] = NotificationAppearance.model_validate(
                        payload["appearance"],
                    )
                result = await notifier.send(payload["content"], targets=(name,), **options)
                if len(result.deliveries) != 1 or result.deliveries[0].target != name:
                    raise NotificationDeliveryError("webhook_invalid_response")
                delivery = result.deliveries[0]
                if not delivery.success:
                    raise NotificationDeliveryError(delivery.error_code, retry_after=delivery.retry_after,
                                               permanent=delivery.permanent)
                message_id = delivery.message_id
                if message_id is not None and (
                    not isinstance(message_id, str) or not 1 <= len(message_id) <= 128
                ):
                    raise NotificationDeliveryError("webhook_invalid_response")
            except NotificationDeliveryError as failure:
                state.update(delivery_failure(state["attempts"], failure, policy=policy, clock=clock))
            except Exception:
                state.update(delivery_failure(
                    state["attempts"], NotificationDeliveryError("webhook_delivery_error"),
                    policy=policy, clock=clock,
                ))
            else:
                state.update(status="sent", attempts=state["attempts"] + 1,
                             message_id=message_id, error_code=None)
        if not await checkpoint(payload=payload):
            return dict(status="processing")
    retrying = [state for state in states.values() if state["status"] not in ("sent", "dead")]
    status = "dead" if any(state["status"] == "dead" for state in states.values()) else "sent"
    return dict(
        payload=payload,
        status="retry" if retrying else status,
        attempts=max((state["attempts"] for state in states.values()), default=0),
        next_attempt_at=min((state["next_attempt_at"] for state in retrying), default=0),
        error_code=next((state["error_code"] for state in states.values() if state["error_code"]), None),
    )
