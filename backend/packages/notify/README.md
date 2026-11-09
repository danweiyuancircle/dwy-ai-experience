# dwy-notify

独立多目标异步通知包，基于 `apprise==2.1.0`，公共配置和结果类型由本包拥有。依赖 `dwyeapi==0.12.1` 基础规范，不要求运行 Webhook 服务。

来源无关的通知集成入口：

- `dwy_notify.events.NotificationEvent`、`EventSink`：已验证事件的接收合同，不包含原始签名或邮件正文。
- `dwy_notify.relay.NotificationRelay`：单次转发和有界成功去重；调用方通过 `appearance` 注入模块名称与可选头像，不按来源猜测业务预设。
- `dwy_notify.delivery`：`DeliveryPolicy`、`NotificationDeliveryError`、`deliver_notifications`、`delivery_failure`，复用逐目标检查点和安全退避；不创建数据库。
- `dwy_notify.sqlalchemy`：通过 `dwy-notify[sqlalchemy]` 安装的 `build_delivery_table`、`SQLAlchemyDeliveryQueue`；会话、表、生命周期、迁移均归宿主，队列显式接收 `appearance`。
- `dwy_notify.integration`：`NotificationSettings`、`configured_notifier` 等目标选择与历史 Discord 配置适配，保留旧 URL 指纹；新集成优先使用 `NotificationConfig`。

基础发送器不依赖 Apple、邮件或 Webhook 业务包。新模块使用自己的展示预设；历史兼容字段的旧名称仅为保证已有队列目标指纹稳定，不作为新业务的默认名称。

0.3.3 新增 `NotificationEvent.appearance` 可选默认展示；relay 优先使用逐事件预设，未传时沿用模块预设。`SQLAlchemyDeliveryQueue` 在入队时将事件展示写入现有 JSON，重启和失败重试保留快照；`enqueue` 与 `enqueue_in_session` 同样接受可选关键字 `appearance`。它只传递展示，不识别 Apple 或其它业务事件。应用配置与目标 URL 的显式展示覆盖优先级不变。

实际 wheel 的发布验收在仓库外执行 `tests/delivery_wheel_smoke.py EXPECTED_VERSION`；需安装 `sqlalchemy` extra 与测试 SQLite 驱动。它核对安装版本、基础导入不加载 ORM/FastAPI/旧业务包，以及队列持久化显式预设和重启去重；不向外部服务发消息。

```bash
pip install dwy-notify==0.3.3
```

```python
import asyncio
import os

from dwy_notify import NotificationAppearance, NotificationConfig, Notifier


async def main() -> None:
    notifier = Notifier(NotificationConfig(
        targets={
            "discord": os.environ["DISCORD_NOTIFY_URL"],
            "wecom": os.environ["WECOM_NOTIFY_URL"],
        },
        appearance=NotificationAppearance(username="业务通知"),
    ))
    result = await notifier.send("任务完成", title="每日汇总")
    for delivery in result.deliveries:
        if not delivery.success:
            print(delivery.target, delivery.error_code, delivery.retry_after, delivery.permanent)


asyncio.run(main())
```

`DISCORD_NOTIFY_URL` 来自宿主环境，可用 `discord://WEBHOOK_ID/WEBHOOK_TOKEN` 或 `https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN`。`WECOM_NOTIFY_URL` 使用 `wecombot://WEBHOOK_KEY`。凭据应来自环境变量或秘密存储，不写入版本库。配置使用 `SecretStr` 隐藏 URL；调用方不要解密后记录。

`NotificationConfig(targets=..., timeout_seconds=10)` 为 frozen Pydantic 模型，目标映射非空，超时必须为有限正数且不超过 30 秒，不接受布尔值。`Notifier` 在构造时固定目标快照，不读取环境变量。`targets` 返回目标名元组，`target_fingerprint(name)` 返回 URL 的 SHA-256 摘要，供调用方检测配置变更；摘要不包含明文 URL。

`await notifier.send(body, title="", targets=None)` 默认发送全部目标，返回 `NotificationResult`。`success` 仅在至少一个目标且全部成功时为真，`succeeded` / `failed` 是目标名元组，详情位于 `deliveries`。每条 `NotificationDelivery` 包含 `target`、`success`、`message_id`、`error_code`、`retry_after`、`permanent`。正文必须为非空白字符串，标题必须为字符串，显式 targets 必须非空且不重复；无效输入或未知目标在发请求前抛出固定 `ValueError`。调用方应遵守 `retry_after` 并排除永久失败，再用失败目标列表重试。

安全边界：

- HTTP 渠道强制 TLS 校验、禁重定向、禁 SDK retry 和 optional 成功；覆盖 URL 中相反选项。普通渠道沿用 Apprise 的 HTTPS 协议和安全参数，不使用全局 monkeypatch。
- Discord 复用上游解析、消息构造和分段，仅适配单次 HTTP 发送：`allowed_mentions={"parse": []}`、始终设置 flags 的 `4` 位，并用 `wait=true` 确认真实消息 ID；响应 ID 必须为 1 至 128 位 ASCII 数字。需要分段时使用 Apprise 的 `?overflow=split`，分段遇失败停止后续请求。企业微信仅在 JSON `errcode` 为整数 `0` 时成功。
- Discord / 企业微信返回 HTTP 状态对应的安全错误码，429 的有效秒数放入 `retry_after`，408 与 5xx 可重试。普通渠道以 SDK 返回值判断成功，失败统一 `send_failed`，不暴露原始响应或异常。插件日志通过本包子类隔离；urllib3 原始 HTTP 日志仅在通知工作线程的发送区间被过滤，宿主其它线程、普通 HTTP 调用与应用日志保留。
- 支持 Apprise 基于 `requests` 的 HTTPS 渠道，例如 Discord、企业微信、钉钉、飞书和 `jsons` 自定义 HTTPS；不支持 SMTP、本地命令等非 HTTP 协议或明文协议，也拒绝固定版本中自带内部重试的 Fluxer、Revolt、Matrix、SparkPost、SendPulse，构造时返回 `unsupported_transport`。可选渠道的额外依赖仍需由宿主安装。
- 同一目标串行，不同目标可并发。取消等待会传播 `CancelledError`；已开始的同步请求在线程中继续，由连接／读取超时结束，同目标锁直到请求结束才释放。超时是 socket 超时，不是整条通知的硬截止时间；上游分段、多接收人或节流可能增加总耗时。
- `Notifier` 不提供持久化、调度或自动重试。分段通知中已经成功的部分可能在调用方整体重试时重复；HTTP 接收后丢失响应也无法保证恰好一次。

仅 Discord、企业微信、钉钉和飞书通过模拟 HTTP 验证；未进行真实渠道投递验收，也未逐一验收全部 Apprise 插件。发布必须通过 GitHub Actions OIDC，不使用长期发布 token。

## 发送者名称与可选头像

`NotificationAppearance(username=..., avatar_url=...)` 只描述平台基础展示，不包含购买、审核等业务预设。每个目标最终必须具有发送者名称；所有配置层都未提供名称时，`send` 在任何目标发出网络请求前抛出 `ValueError("missing_username")`。正文 `title` 不能代替发送者名称。头像可省略，沿用平台默认头像，不注入 Apprise Logo。

应用在 `NotificationConfig.appearance` 设置默认展示；单次 `send(..., appearance=...)` 可覆盖；具体业务库通过 `send(..., default_appearance=...)` 提供低优先级预设。按字段选择：单次设置 > 应用配置 > 目标 URL 的显式名称/头像 > 业务预设。未设置字段继承；名称不能显式设为 `None` 或空白，头像可通过 `avatar_url=None` 清除预设、恢复平台默认。仅覆盖头像时，名称继续从应用或具体模块继承。

名称限制为 1–80 字符且不包含控制字符；图片 URL 限长 2048，要求 HTTPS 且不携带账号密码。图片须由平台匿名访问，不接受本地路径，不在应用发送进程中下载图片。当前 Discord 适配使用这些字段，其它渠道保留自身展示行为。展示不参与目标 URL 指纹，不改变接收方去重或发送重试。

兼容层若把隐式默认名称编码进旧 URL，构造 `Notifier(..., url_appearance_is_default=True)` 可让这些展示字段退到业务预设之后，同时保留原目标 URL 与指纹；真实用户显式设置的 URL 保持默认优先级。

## 追加公开展示字段

`NotificationField` 与 `render_notification_fields` 从 `dwy_notify` 根导出，用于给正文追加少量业务标签。宿主先从用户、订单等对象中筛选公开字符串，再构造字段；不要传完整对象、凭据或个人敏感信息。它们不读取数据库或网络，不修改官方回调数据，也不改变 `send` 和队列接口。

```python
from dwy_notify import NotificationField, render_notification_fields

body = "支付成功"
fields = (
    NotificationField(label="来源", value="网站"),
    NotificationField(label="套餐", value="专业版"),
)
# 2048 是宿主选定的正文总预算，额外预留一个拼接换行的 UTF-8 字节。
extra = render_notification_fields(fields, max_bytes=2048 - len(body.encode("utf-8")) - 1)
content = f"{body}\n{extra}" if extra else body
```

模型冻结、拒绝额外属性，`label` / `value` 必须为严格字符串，分别为 1–32 / 1–256 个字符，不能全为空白，也不能包含控制字符、格式控制字符（含双向文本控制和零宽连接符）、孤立代理项或 Unicode 行分隔符。校验错误的文本不回显输入；调用方记录 Pydantic 结构化错误时仍须移除 `input`。

渲染接收最多八个 `NotificationField` 的元组，保留顺序，每行采用「标签：值」。`max_bytes` 必须是整数（不接受布尔），表示本段剩余 UTF-8 字节预算；正文、标题、分隔符由宿主另外预留。值截短后加 `…`，其余字段放不下时加 `[已省略]`；标签不会截短，提示也放不下时返回空串，零或负预算同样返回空串。字段数量、类型或预算类型无效时抛出固定原因码 `ValueError`，不会回显内容。

输出沿用当前传输：企业微信发送 `text.content`，不添加 `mentioned_list` / `mentioned_mobile_list`，Markdown 和 `@all` 为普通文本；Discord 的 `allowed_mentions={"parse": []}` 继续禁用提醒。渲染器不添加 Markdown 转义，不提供跨所有 Apprise 渠道的富文本安全保证。

## 与业务共用事务及失败重放

`SQLAlchemyDeliveryQueue` 通过 `dwy-notify[sqlalchemy]` 使用 PostgreSQL 或 SQLite。`enqueue` 继续创建并提交独立事务；需要与支付、订单等业务状态同时提交时，调用 `enqueue_in_session(db, app_id, event_id, event_type, content)`。`db` 是宿主的 `AsyncSession`，队列不会 begin、commit、rollback 或 close 它。返回 `True` 表示新入队，`False` 表示同一 `(app_id, event_id)` 已存在；冲突忽略不会使外层事务失效。

```python
from dwy_notify.sqlalchemy import SQLAlchemyDeliveryQueue
from sqlalchemy.ext.asyncio import AsyncSession


async def enqueue_payment_notice(
    db: AsyncSession, queue: SQLAlchemyDeliveryQueue, order_id: str, content: str,
) -> bool:
    """由宿主把业务更新和本次入队一同提交，异常时一同回滚。"""
    return await queue.enqueue_in_session(db, "payments", order_id, "payment.paid", content)


async def replay_failed_notice(
    db: AsyncSession, queue: SQLAlchemyDeliveryQueue, order_id: str,
) -> bool:
    """宿主完成操作者鉴权与审计后，仅重放账本中失败的指定目标。"""
    return await queue.requeue_failed_in_session(db, "payments", order_id, ("wecom",))
```

scope 非空白且不超过注入表 `app_id` 的长度（默认 128）；`event_id`、`event_type` 非空白且不超过 128 字符；正文非空白且最多 65536 字符。内容完整保留，超限拒绝，不截断。`ValueError` 仅包含固定原因码，不回显标识、正文或目标 URL。

`allowed_scopes` 限制消费者领取范围：`None` 领取全部 scope，空集合不领取；显式集合只处理其中的 scope。同表其它 scope 的积压正文、状态和租约保持原样，不会因当前消费者的配置被清除。

`requeue_failed_in_session` 要求队列注入 `notifier`，`targets` 为非空、不重复的目标名元组。只把指定的 `dead` / `retry` 目标重置为 `pending`、尝试次数 0、当前时刻可发；父记录重新聚合调度与失败状态。正文、展示快照、原目标指纹及其它目标的状态保持不变；当前配置新增的目标不会收到历史消息。无记录、尚未初始化目标快照或选中目标没有失败状态时返回 `False`。

成功目标抛出 `notification_target_sent`；快照中不存在的目标抛出 `notification_target_not_in_snapshot`；当前已移除或指纹变化的目标分别抛出 `notification_target_missing` / `notification_target_changed`；活跃父租约抛出 `notification_active_lease`。先验证全部选择再重置，混合选择不会部分生效。重放自身不发送消息，由既有消费者在事务提交后处理；外层回滚会撤销重放。该接口持有数据库写锁直到宿主提交或回滚，宿主应及时结束事务；SQLite 需要支持 `RETURNING` 的 3.35 及以上版本。

过期租约的 token 会在重放时清除，旧消费者无法覆盖新状态。网络已接收但响应丢失的失败记录仍可能在重放后产生重复消息，沿用原投递语义。
