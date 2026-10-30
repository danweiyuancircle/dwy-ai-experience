"""可移植的 App Store Server Notifications V2 接收与官方验签边界。"""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from dwy_notify.events import EventSink
from dwy_notify.events import NotificationEvent as WebhookEvent
from fastapi import APIRouter, HTTPException, Request

from ..config import AppleNotificationApp, AppleNotificationsConfig
from ..errors import WebhookVerificationError
from . import accept_event, read_payload
from .apple_content import apple_notification_content
from .apple_models import (
    VerifiedAppleNotification,
    _date,
    apple_refund_request_reason,
    apple_renewal_details,
    apple_transaction_details,
)


def _text(value, *, maximum: int = 255) -> str:
    """约束已验签字段的结构，不把 SDK 的 None 或任意对象直接转成文本。"""
    value = getattr(value, "value", value)
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        raise ValueError("invalid notification field")
    return value


class AppleNotificationVerifier:
    """每个配置应用独占官方 verifier；签名线程与在途任务均有上限。"""

    def __init__(self, config: AppleNotificationApp):
        """生产必须声明 App Apple ID；根证书字节由调用项目显式注入。"""
        if config.environment == "Production" and config.app_apple_id is None:
            raise ValueError("Production Apple notifications require app_apple_id")
        self.config = config
        self._verifier = None
        self._closed = False
        self._executor = ThreadPoolExecutor(
            max_workers=config.verification_workers, thread_name_prefix="webhook-apple-verify"
        )
        self._semaphore = asyncio.Semaphore(config.verification_workers)
        self._pending: set[asyncio.Future] = set()

    def _sdk(self):
        """延迟构造 SDK，缺失能力和证书错误仅返回固定的不可用分类。"""
        if self._closed:
            raise WebhookVerificationError("apple_verifier_closed", status_code=503)
        if self._verifier is None:
            try:
                from appstoreserverlibrary.models.Environment import Environment
                from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier

                roots = list(self.config.root_certificates)
                if not roots:
                    raise ValueError("missing roots")
                self._verifier = SignedDataVerifier(
                    roots, self.config.enable_online_checks, Environment(self.config.environment),
                    self.config.bundle_id, self.config.app_apple_id,
                )
            except (ImportError, OSError, ValueError):
                raise WebhookVerificationError("apple_verifier_unavailable", status_code=503) from None
        return self._verifier

    async def _verify(self, method: str, signed: str):
        """取消等待不提前释放在途预算，防止慢在线检查堆积无限线程池任务。"""
        if not isinstance(signed, str) or not 1 <= len(signed) <= 131072:
            raise WebhookVerificationError("apple_signature_invalid")
        verifier = self._sdk()
        await self._semaphore.acquire()
        if self._closed:
            self._semaphore.release()
            raise WebhookVerificationError("apple_verifier_closed", status_code=503)
        future = asyncio.get_running_loop().run_in_executor(self._executor, getattr(verifier, method), signed)
        self._pending.add(future)

        def finished(done):
            """实际签名工作完成才释放预算，并消费被取消调用者留下的异常。"""
            self._pending.discard(done)
            self._semaphore.release()
            if not done.cancelled():
                done.exception()

        future.add_done_callback(finished)
        try:
            return await asyncio.shield(future)
        except Exception as error:
            from appstoreserverlibrary.signed_data_verifier import VerificationException, VerificationStatus

            if (isinstance(error, VerificationException)
                    and error.status == VerificationStatus.RETRYABLE_VERIFICATION_FAILURE):
                raise WebhookVerificationError("apple_verification_unavailable", status_code=503) from None
            raise WebhookVerificationError("apple_signature_invalid") from None

    async def verify(self, signed_payload: str) -> VerifiedAppleNotification:
        """外层通知和每个嵌套 JWS 分别验签，再检查交易关系与元数据结构。"""
        notice = await self._verify("verify_and_decode_notification", signed_payload)
        try:
            data = notice.data
            target = data or notice.summary or getattr(notice, "appData", None)
            external = getattr(notice, "externalPurchaseToken", None)
            if target is None:
                target = external
            if target is None:
                raise ValueError("missing notification identity")
            bundle_id = _text(target.bundleId)
            if target is external:
                environment = ("Sandbox" if (external.externalPurchaseId or "").startswith("SANDBOX")
                               else "Production")
            else:
                environment = _text(target.environment, maximum=32)
            if bundle_id != self.config.bundle_id or environment != self.config.environment:
                raise ValueError("notification identity mismatch")
            if self.config.environment == "Production" and target.appAppleId != self.config.app_apple_id:
                raise ValueError("notification application mismatch")
            transaction = None
            renewal = None
            if data and data.signedTransactionInfo:
                transaction = await self._verify(
                    "verify_and_decode_signed_transaction", data.signedTransactionInfo
                )
                if (_text(transaction.bundleId) != bundle_id
                        or _text(transaction.environment, maximum=32) != environment):
                    raise ValueError("transaction identity mismatch")
            if data and data.signedRenewalInfo:
                renewal = await self._verify("verify_and_decode_renewal_info", data.signedRenewalInfo)
                if transaction:
                    original = _text(transaction.originalTransactionId, maximum=128)
                    if _text(renewal.originalTransactionId, maximum=128) != original:
                        raise ValueError("transaction renewal mismatch")
            return VerifiedAppleNotification(
                notification_id=_text(notice.notificationUUID, maximum=128), bundle_id=bundle_id,
                environment=environment, notification_type=_text(notice.notificationType, maximum=100),
                signed_at=_date(notice.signedDate),
                subtype=_text(notice.subtype, maximum=100) if notice.subtype is not None else None,
                product_id=_text(transaction.productId) if transaction is not None else None,
                transaction_id=(_text(transaction.transactionId, maximum=128)
                                if transaction is not None else None),
                transaction_details=(
                    apple_transaction_details(transaction) if transaction is not None else None
                ),
                renewal_details=apple_renewal_details(renewal) if renewal is not None else None,
                consumption_request_reason=apple_refund_request_reason(data) if data is not None else None,
            )
        except (AttributeError, TypeError, ValueError, OverflowError, OSError):
            raise WebhookVerificationError("apple_notification_invalid") from None

    async def aclose(self) -> None:
        """关闭后拒绝新工作，等待有界签名任务退出并回收线程资源。"""
        if self._closed:
            return
        self._closed = True
        try:
            if self._pending:
                await asyncio.gather(*tuple(self._pending), return_exceptions=True)
        finally:
            self._executor.shutdown(wait=False, cancel_futures=True)


def _content(name: str, notice: VerifiedAppleNotification) -> str:
    """保留既有内部入口，通用 router 和业务自有队列使用同一文案规则。"""
    return apple_notification_content(notice, app_name=name)


def create_apple_router(
    config: AppleNotificationsConfig, sink: EventSink, verifiers: dict[str, AppleNotificationVerifier],
) -> APIRouter:
    """安装来源路由；verifier 由注册器持有并在宿主关闭时回收。"""
    router = APIRouter()

    @router.post(config.path, include_in_schema=False)
    async def receive(app_id: str, request: Request):
        """先定位固定配置，再限流读取和完整验签，最后投递已选事件。"""
        application = config.apps.get(app_id)
        verifier = verifiers.get(app_id)
        if application is None or verifier is None:
            raise HTTPException(404, "Webhook is not configured")
        raw = await read_payload(request, max_bytes=262144)
        try:
            body = json.loads(raw)
            signed = body.get("signedPayload") if isinstance(body, dict) else None
            if not isinstance(signed, str) or not 1 <= len(signed) <= 131072:
                raise ValueError("invalid signed payload")
        except (ValueError, UnicodeError):
            raise HTTPException(400, "Invalid Apple notification") from None
        try:
            notice = await verifier.verify(signed)
        except WebhookVerificationError as error:
            raise HTTPException(error.status_code, "Apple notification verification failed") from None
        if config.events is not None and notice.notification_type not in config.events:
            return {"received": True, "ignored": True}
        event = WebhookEvent(
            source="apple_notifications", scope=app_id, event_id=notice.notification_id,
            event_type=notice.notification_type, content=_content(application.name, notice),
            data=notice.public_data(),
        )
        return await accept_event(sink, event)

    return router
