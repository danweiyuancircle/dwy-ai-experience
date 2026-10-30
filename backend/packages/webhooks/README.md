# dwy-webhooks

## 模块展示预设

业务展示由各模块拥有：Apple 购买为「购买通知」、ASC 为「应用审核通知」、经营日报/周报为「经营报表」、Resend 为「邮件通知」，其它来源共用「系统通知」。模块预设不下沉到 dwy-notify。独立宿主队列可以通过 `dwy_webhooks.appearance.notification_appearance(source)` 获取同一预设，并传给 `deliver_notifications(..., appearance=...)`。

五张 PNG、SVG 源图和 Lucide 许可维护在 `backend/packages/webhooks/assets/`；默认公网地址固定到资产提交 `091ad4fea18ed3840fec83dc833f18b759256ca7`，例如 `https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/091ad4fea18ed3840fec83dc833f18b759256ca7/backend/packages/webhooks/assets/purchase.png`。Discord 自行读取公开图片，各应用不需要部署图片服务。

应用可在各来源的 `notifications.appearance` 设置 `username` 和 `avatar_url`，覆盖单个字段或整套预设；`avatar_url: null` 使用平台默认头像。现有目标 URL 中显式配置的展示也优先于模块默认值。直接转发和持久队列共用预设；首次发送前把预设写入现有 JSON outbox，失败重试保留原预设，无需数据库迁移。

## Apple 经营日报与周报

`dwy-webhooks[analytics]==0.6.2` 提供公开的 `dwy_webhooks.analytics`。默认北京时间 `Asia/Shanghai` 每天 08:30，固定统计发送日期前两天的数据（如 30 日取 28 日、31 日取 29 日），为 Apple UTC 报表预留生成时间；周一附加截至前两天的连续七天周报。未发布或不可用的指标按状态展示，不等待或自动补发旧日报。

调用项目注入 `AppleAnalyticsConfig`、会话及 `build_analytics_tables(metadata)` 的表定义，再使用 `install_analytics_monitor(app, config, sessions, tables)` 安装。数据库迁移和 engine 生命周期仍由项目拥有；示例见 `backend/packages/webhooks/examples/new_project/analytics.py`。

指标包含官方可取得的首次/重新下载、曝光与页面访问事件次数、USD 估算销售/收益/退款、订阅状态/新增/续费/流失、地区与来源。缺报及未取得的维度不会补零。跨行 Unique Counts 不能用来拼接官方下载转化率；MRR、留存、去重付费用户及付费 cohort 未经验证不计算。

`AppleAnalyticsClient.initialize(app_id)` 显式申请 ONGOING 报表，不在常驻采集时自动升级权限。初次生成需要等待；报告原始统计日独立于通知发送时区。API Bearer 不传给报表下载地址，网络读取与 gzip/TSV 解析均有预算。

运行时使用账号/App 隔离的持久租约，日期快照和 outbox 同事务提交，复用统一通知发送与逐目标重试。近七天修正替换旧快照；重启不补发所有历史日报；网络确认丢失仍存在重复送达窗口。可选 `feedback(app_id, date)` 回调提供文字评论计数，不依赖评论模块或 App Cloud。

`ReviewStore.summary(app_id, day)` 返回已采集完整 UTC 创建日的 `review_count`、`low_star_reviews`；无完整基线、未来或已清理日期返回空映射。该摘要不是商店全部星级，不包含正文或昵称。

基于 EAPI 的通用 Webhook 模块。接收 Resend、App Store Connect、Apple Server Notifications V2，并按项目配置通过 `dwy-notify` 转发到配置的通知目标或外部注入的业务接收函数；也支持主动采集 App Store 文字评论及星级。

## 安装与依赖

核心依赖固定兼容版本 `dwyeapi==0.12.1` 与 `dwy-notify==0.2.0`；平台 SDK 按需选择 `dwy-webhooks[resend,apple]`，评论与经营采集分别选择 `reviews`、`analytics`。旧 `discord` extra 保留为空，不安装 `discord-webhook` SDK。ASC Webhook 使用标准库 HMAC；只有 Apple Server Notifications 需要 Apple SDK。源码由 dwy-shared 维护，项目安装独立 wheel，不引用共享仓库的绝对源码路径。发布配置不表示已经发布。

## 统一通知配置（0.6.0）

`NotificationConfig(targets={目标名: SecretStr或字符串}, timeout_seconds=10)` 使用显式传入的 Apprise URL。Discord 形如 `discord://Mail@WEBHOOK_ID/WEBHOOK_TOKEN`，企业微信机器人形如 `wecombot://BOT_KEY`；其它已支持的 Apprise HTTPS 渠道尽量只改配置。URL 由宿主密钥配置注入，日志和队列不保存明文 URL。直接通知也能在普通 Python 程序使用：

```python
from dwy_notify import NotificationConfig, Notifier

async def notify(targets: dict[str, str]) -> bool:
    """targets 由宿主配置注入；结果按目标汇总，失败不会被当成成功。"""
    result = await Notifier(NotificationConfig(targets=targets)).send("任务已完成", title="任务通知")
    return result.success
```

`result.deliveries` 保留每个目标的结果、消息 ID、安全错误码和重试信息；`succeeded`、`failed` 是目标名元组。`send(..., targets=("mail",))` 可显式选择配置内目标。SDK 类型不出现在公开 API。

当前支持基于 `requests` 的 HTTPS 渠道；SMTP、本地命令、明文协议及带不可禁用内部重试的插件会在构造时拒绝，具体边界见 `backend/packages/notify/README.md`。普通渠道以 SDK 返回值判断成功，失败统一为安全的 `send_failed`；可能需要宿主补装渠道可选依赖。取消等待会传播，但已开始的同步请求仍在线程中由 socket 超时结束；分段或多接收人通知没有整条硬截止，整体重试可能重复已成功片段。

Webhook 全局 `notifications` 仅作默认值，Resend、ASC、Apple 来源各自的 `notifications` 可覆盖。评论的 `AppleReviewsConfig.notifications` 和日报的 `AppleAnalyticsConfig.notifications` 独立配置；例如评论只发 Discord，日报同时发 Discord 和企业微信。各安装器只读取自己的配置，不要求安装另一个功能或额外注入 Notifier；自定义 sink / sender 仍有最高优先级。完整装配示例见 `backend/packages/webhooks/examples/new_project/notifications.py`。

旧 `discord_webhook_url` / `discord_username` 和 `DiscordWebhookSender` 保留兼容，内部同样转调 `dwy-notify`，没有第二套发送 SDK。新配置用 URL 的用户名设置渠道名称；同一层不能同时配置新旧目标，模型会拒绝。来源配置可以覆盖全局默认。

持久队列将逐目标状态、次数、下次重试时间和目标指纹写进既有 payload JSON，无需 schema 迁移；已成功目标不会随失败目标重发。旧待发载荷首次处理时绑定当时目标，之后目标删除或 URL 改变不会把旧消息静默投给新接收方。部分永久失败仍保留其它目标的成功状态；网络成功但确认丢失仍可能重复送达。

## Apple 内购详情与通知

安装 `dwy-webhooks[apple]==0.6.1` 即可在其他 FastAPI 项目使用，不需要 App Cloud、ADBox、账户或商品权益表：

```python
from fastapi import FastAPI
from dwy_notify import NotificationConfig
from dwy_webhooks import WebhookConfig, install_webhooks
from dwy_webhooks.config import AppleNotificationApp, AppleNotificationsConfig


def create_app(apple_id: int, certificates: tuple[bytes, ...], discord_url: str) -> FastAPI:
    """discord_url 是宿主提供的 Apprise URL；证书传字节。"""
    app = FastAPI()
    install_webhooks(app, WebhookConfig(
        notifications=NotificationConfig(targets={"purchases": discord_url}),
        apple_notifications=AppleNotificationsConfig(apps={
            "my-app": AppleNotificationApp(
                name="My App", bundle_id="com.example.myapp", environment="Production",
                app_apple_id=apple_id, root_certificates=certificates,
            ),
        }),
    ))
    return app
```

Apple V2 回调路径为 `/webhooks/apple/my-app`。旧 Discord 配置默认发送者为「Apple 应用通知」，`AppleNotificationsConfig.discord_username` 可覆写；新通知 URL 用用户名配置名称。应用名称由 `AppleNotificationApp.name` 注入。默认注册器的去重及可注入持久 sink 语义沿用原接口。

通知展示交易金额/币种、购买店面、时间、本人购买/家庭共享、退款申请的用户选择分类、退款结果的 Apple 分类及适用续订设置。金额按整数毫单位精确换算，退款仅展示原交易价格；缺失显示未提供，未知分类保留代码，不推断用户自由文本、开发者收入或购买设备平台。

已有业务队列可使用公开 `dwy_webhooks.apple`：`AppleNotificationVerifier`、`VerifiedAppleNotification`、`AppleTransactionDetails`、`AppleRenewalDetails` 和 `apple_notification_content(notice, app_name="My App")`；格式化后的字符串直接交既有 `DiscordWebhookSender`，其 `username` 可覆写。`apple_transaction_details`、`apple_renewal_details` 和 `apple_refund_request_reason` 只消费已经完成官方验签的 SDK 对象，本身不代替验签。

`VerifiedAppleNotification` 保留原八字段构造及 `public_data()` 白名单，新增可选 `transaction_details`、`renewal_details`、`consumption_request_reason`。详情模型不包含账户 token、原始 JWS、签名摘要或权益策略。商品白名单、账户绑定、持久化及申请退款不提前撤销权益等业务规则仍由宿主管理。

PyPI 从此版本起只上传 `py3-none-any.whl`；通用 wheel 含可读 Python 模块，不提供源码隐藏。源码包只参与内部归档检查，不上传 PyPI。

## 配置与接入

### ASC 审核通知的平台与版本

审核事件本身只包含状态变化和 `appStoreVersions` 资源 ID；载荷里的 `version: 1` 不是应用版本号。安装 `dwy-webhooks[asc]` 并显式配置 `AppStoreConnectWebhookConfig.api` 后，适配器会按事件中的具体版本 ID 查询 `platform` 与 `versionString`，校验所属 App，再将平台、版本号补入通知。查询结果的最新审核状态不会覆盖事件原始状态。

```python
from pydantic import SecretStr

from dwy_webhooks.config import (
    AppStoreConnectAPIConfig,
    AppStoreConnectApp,
    AppStoreConnectWebhookConfig,
)


def asc_config(
    *, apps: dict[str, AppStoreConnectApp], issuer_id: str, key_id: str, private_key: SecretStr,
) -> AppStoreConnectWebhookConfig:
    """参数由宿主 Settings 提供；API 账号凭据与各 App 的 HMAC 密钥分别注入。"""
    return AppStoreConnectWebhookConfig(
        apps=apps,
        api=AppStoreConnectAPIConfig(issuer_id=issuer_id, key_id=key_id, private_key=private_key),
    )
```

宿主可以显式复用已有评论或经营报表的 ASC 账号凭据；无需启用这些功能，也不由库读取其他模块或环境。所用密钥需要有权读取该 App 的版本信息，Webhook 签名密钥不能代替 ASC API 账号凭据。

查询使用固定地址 `https://api.appstoreconnect.apple.com/v1/appStoreVersions/{id}`，不跟随重定向，限制超时和响应体积。查询失败返回 502，留给 Apple 重投，不确认或发送缺少详情的完整事件；未配置 API 的旧接入仍接收通知，但平台、版本明确标记“未查询（未配置 ASC API）”。构建上传事件和官方 ping 不触发版本查询。无需数据库迁移。

库不读取环境变量、`.env`、项目设置或证书文件。`WebhookConfig` 是纯 Pydantic 模型；项目可组合进自己的 EAPI Settings。密钥由项目取得后传入，Apple 根证书传入字节。

```python
from dwy_notify import NotificationConfig
from dwy_webhooks import WebhookConfig, install_webhooks
from dwy_webhooks.config import AppleNotificationsConfig, ResendWebhookConfig

# project_settings 由宿主取得密钥；URL 为 Apprise 格式，不写进源码。
config = WebhookConfig(
    notifications=NotificationConfig(targets=project_settings.default_notification_targets),
    resend=ResendWebhookConfig(
        secret=project_settings.resend_webhook_secret,
        name="My Project", events=frozenset({"email.received", "email.failed"}),
        notifications=NotificationConfig(targets={
            "mail": project_settings.discord_notification_url,
        }),
    ),
    apple_notifications=AppleNotificationsConfig(
        apps=project_settings.apple_notification_apps,
        notifications=NotificationConfig(targets={
            "purchases": project_settings.wecom_notification_url,
        }),
    ),
)
runtime = install_webhooks(app, config)
```

Resend 使用 Webhook 签名密钥，不使用发送邮件的 API Key。未配置来源不注册路由；各来源可独立覆盖通知目标、事件集合和接收路径。

- `AppStoreConnectWebhookConfig(apps={app_id: AppStoreConnectApp(name=..., secret=...)})` 配置审核、构建及 ping 通知。
- `AppleNotificationsConfig(apps={key: AppleNotificationApp(name=..., bundle_id=..., environment="Production", app_apple_id=..., root_certificates=(certificate_bytes, ...))})` 配置 Server Notifications V2。
- 将前两者放入 `WebhookConfig.app_store_connect`、`.apple_notifications` 后，一次注册即可接入。
- 默认路径：`/webhooks/resend`、`/webhooks/app-store-connect/{app_id}`、`/webhooks/apple/{app_id}`；完整公开 URL 由项目域名及反向代理决定。

## 资源与接收语义

- 默认 relay 在全部目标发送成功后确认，实例内保留有界去重记录，部分失败仅重试未成功目标。失败返回非 2xx 供提供方重试；重启可能再次发送，不承诺持久或恰好一次投递。
- 项目可注入 `ReceiptStore`，或通过 `WebhookSinks` 按来源注入接收函数。函数接收已验证的 `WebhookEvent`，返回 True 表示接受、False 表示重复；异常不能被确认成功。
- `SQLAlchemyDeliveryQueue` 提供持久队列，sessions、table、sender、source 和可选策略由外部注入。使用 EAPI 创建的会话，不创建、迁移或关闭项目数据库。一个表固定一个来源，防止跨来源编号碰撞。
- 已有其它队列表结构可直接使用 `dwy_webhooks.notification_delivery.deliver_notifications(notifier, payload, *, policy, clock, checkpoint)`，复用同一逐目标算法。`payload` 是当前记录独立解码的可变字典，含 `content` 和可选的 `notifications` 状态；其它宿主字段保留。`checkpoint(**values)` 必须按当前租约原子持久化 `payload` 或续租 `lease_until`，成功返回 True；False 会停止并返回 `{"status": "processing"}`，调用方不得把它标记成功或清除新租约。正常返回的聚合状态仍须由调用方按租约提交；取消及检查点异常直接传播。`delivery_failure(attempts, failure, *, policy, clock)` 复用相同的有界退避与安全错误码，不执行持久化。
- `build_delivery_table` 注册到项目 metadata，由项目自己的 Alembic 管理 schema。库不在注册路由时自动建表。
- `install_webhooks` 保留宿主生命周期，只关闭自己拥有的验证器；`create_app(config)` 可建立独立 ASGI 应用，配置仍然必填。普通错误复用 EAPI，第三方成功 ACK 保持提供方协议。

```python
from dwy_webhooks import WebhookSinks, install_webhooks

# persist_verified_event 是项目自己的持久入口，或已注入资源的队列实例。
install_webhooks(app, config, sinks=WebhookSinks(app_store_connect=persist_verified_event))
```

Apple 商品目录、账户绑定和权益发放保留在业务项目。通用模块只验证通知并提供安全事件元数据，不把测试通知或续订设置变更报告为收入。

## 安全和扩展

来源分别验签，并在读取原始字节时限制体积。Apple 外层、交易及续订 JWS 分别走官方 SDK，生产强制 App Apple ID。Discord 固定官方 HTTPS 地址，拒绝重定向和 mentions，等待有效消息编号；错误不记录 token 或原始响应正文。

新增来源增加 provider；通知渠道通过 `dwy-notify` 的 Apprise URL 选择，SDK 异常与安全修正集中在通知包。注册入口不覆盖项目已有的全局异常或缓存配置。

`examples/new_project/app.py` 是不依赖 App Cloud 的接入示例。隔离 wheel 验收要求 `app_cloud`、`apple_iap`、`cloud_kernel`、旧 `cloud_webhooks` 和产品包缺席，公共配置、注册和三类来源仍能通过测试。

## App Store 评论定时通知

`dwy_webhooks.reviews` 提供主动采集能力，独立于审核/构建 Webhook 和内购通知。评论通知安装 `dwy-webhooks[reviews]`：`reviews` 直接声明 HTTPX、PyJWT 和 cryptography，使用账号 API 密钥签发 ES256 JWT 并访问 ASC REST API；不需要 Apple Server SDK 或 Resend SDK，也不依赖其它包偶然传入 PyJWT。无需 Redis 服务、ARQ Worker 或新增调度框架。

```bash
uv add 'dwy-webhooks[reviews]==0.6.1'
```

```python
from sqlalchemy import MetaData
from dwy_notify import NotificationConfig
from dwy_webhooks.reviews import AppleReviewsConfig, build_review_tables, install_review_monitor

# project_settings、EAPI 创建的 sessions 及 app 都由消费项目提供。
config = AppleReviewsConfig(
    apps=project_settings.review_apps,
    issuer_id=project_settings.apple_issuer_id,
    key_id=project_settings.apple_key_id,
    private_key=project_settings.apple_private_key,
    notifications=NotificationConfig(targets=project_settings.review_notification_targets),
    poll_interval_seconds=3600,
    retention_days=30,
)
metadata = MetaData()
tables = build_review_tables(metadata)
# 先通过消费项目的 Alembic 创建上述三张表，再启动任务；库不自动建表。
runtime = install_review_monitor(app, config, sessions, tables)
```

- 默认每小时采集一次，可配置 `poll_interval_seconds`（60–604800 秒）；FastAPI lifespan 管理 asyncio 后台任务。每分钟只检查数据库计划和执行清理，不代表每分钟请求 Apple。
- 每个应用持久化下次执行时间和租约；多消费者不会同时提交同一轮。重启保留计划，失败一分钟后尝试恢复；完整分页失败不会推进基线。
- 每轮完整读取全部评论历史，最多 100 页、每页 200 条，每页响应不超过 2 MiB；整轮同步最长 120 秒。超过这些上限会失败并保留原有基线，不能把它视为只拉取最近 N 天；`retention_days` 控制数据库保留范围。
- 首次只建立保留期内历史基线并发送一条摘要；随后新评论或改文/改星产生通知。通知截断到 Discord 限长，完整原文存于保留期内的数据库记录。
- `retention_days` 默认 30，允许 1–3650（包括 60/90）。按 Apple 评论创建时间保留最近 N 天；评论原文、指纹及该评论的投递载荷都会清理。基线摘要按生成时间清理，最小的应用调度/基线状态长期保留，其中没有评论正文或昵称。
- 扩大保留期时静默补入较老历史，避免当作新评论刷屏；既有保留窗口内的新评论、修改仍通知。已超出窗口的旧评论修改不追踪。
- 清理独立于 Apple 拉取成功与否；投递前也检查过期状态。持久队列提供有界重试，不承诺网络超时场景下恰好一次送达。
- 表、会话、时钟、HTTP 客户端和 sender 可显式注入；库不读取 `.env`、打开项目数据库或自动执行迁移。关闭任务后才允许宿主释放数据库。
- 本功能读取文字评论及其附带星级，不提供纯星级逐条事件、总评分统计或 Discord 内回复。

本轮清单版本为 `0.6.1`，不代表已发布到公开 PyPI。消费项目应在发布完成后固定版本并验收实际安装产物。

## Discord 发送者名称

旧配置的发送者默认使用「Apple 应用通知」，通过 Discord 原生 `username` 字段逐条指定，不修改平台侧 Webhook 配置。调用项目可按自己的场景覆写：

```python
sender = DiscordWebhookSender(webhook_url, username="团队评分通知")
# 评分安装器自动使用此名称；传入自定义 sender 时由该 sender 决定名称。
config = AppleReviewsConfig(
    apps=apps, issuer_id=issuer_id, key_id=key_id, private_key=private_key,
    discord_webhook_url=webhook_url, discord_username="团队评分通知",
)
```

`WebhookConfig.discord_username` 设置通用来源的名称；`ResendWebhookConfig`、`AppStoreConnectWebhookConfig` 和 `AppleNotificationsConfig` 的同名字段可逐来源覆写，省略时继承全局值。邮件等非 Apple 场景应显式设置合适名称。名称必须为 1–80 字符，不能全为空白或包含控制字符。

评分正文以加粗标题区分监控启用、新增和更新，独立展示应用名称与五颗可视星级。调用项目继续管理凭据、数据库连接和 Alembic 迁移，复用时无需复制评分源码。
