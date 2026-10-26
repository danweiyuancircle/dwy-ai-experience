# dwy-webhooks

基于 EAPI 的通用 Webhook 模块。接收 Resend、App Store Connect、Apple Server Notifications V2，并按项目配置转发到 Discord 或外部注入的业务接收函数；也支持主动采集 App Store 文字评论及星级。

## 安装与依赖

核心依赖固定兼容版本 `dwyeapi`；平台 SDK 按需选择 `dwy-webhooks[discord,resend,apple]`，主动评论采集单独选择 `reviews`。ASC Webhook 使用标准库 HMAC；只有 Apple Server Notifications 需要 Apple SDK。源码由 dwy-shared 维护，项目安装独立 wheel，不引用共享仓库的绝对源码路径。发布配置不表示已经发布。

## 配置与接入

库不读取环境变量、`.env`、项目设置或证书文件。`WebhookConfig` 是纯 Pydantic 模型；项目可组合进自己的 EAPI Settings。密钥由项目取得后传入，Apple 根证书传入字节。

```python
from dwy_webhooks import WebhookConfig, install_webhooks
from dwy_webhooks.config import ResendWebhookConfig

# app 与 project_settings 都属于调用项目；库不再回读环境。
config = WebhookConfig(
    discord_webhook_url=project_settings.discord_webhook_url,
    resend=ResendWebhookConfig(
        secret=project_settings.resend_webhook_secret,
        name="My Project", events=frozenset({"email.received", "email.failed"}),
    ),
)
runtime = install_webhooks(app, config)
```

Resend 使用 Webhook 签名密钥，不使用发送邮件的 API Key。未配置来源不注册路由；各来源可独立覆盖 Discord 目标、事件集合和接收路径。

- `AppStoreConnectWebhookConfig(apps={app_id: AppStoreConnectApp(name=..., secret=...)})` 配置审核、构建及 ping 通知。
- `AppleNotificationsConfig(apps={key: AppleNotificationApp(name=..., bundle_id=..., environment="Production", app_apple_id=..., root_certificates=(certificate_bytes, ...))})` 配置 Server Notifications V2。
- 将前两者放入 `WebhookConfig.app_store_connect`、`.apple_notifications` 后，一次注册即可接入。
- 默认路径：`/webhooks/resend`、`/webhooks/app-store-connect/{app_id}`、`/webhooks/apple/{app_id}`；完整公开 URL 由项目域名及反向代理决定。

## 资源与接收语义

- 默认 `DiscordRelay` 在发送成功后确认，实例内保留最多 4096 条成功记录。失败返回非 2xx 供提供方重试。重启可能再次发送，这不是持久或恰好一次投递保证。
- 项目可注入 `ReceiptStore`，或通过 `WebhookSinks` 按来源注入接收函数。函数接收已验证的 `WebhookEvent`，返回 True 表示接受、False 表示重复；异常不能被确认成功。
- `SQLAlchemyDeliveryQueue` 提供持久队列，sessions、table、sender、source 和可选策略由外部注入。使用 EAPI 创建的会话，不创建、迁移或关闭项目数据库。一个表固定一个来源，防止跨来源编号碰撞。
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

新增来源增加 provider，新增目标增加 transport；共用事件、sink 和 EAPI 资源，避免平台大分支。注册入口不覆盖项目已有的全局异常或缓存配置。

`examples/new_project/app.py` 是不依赖 App Cloud 的接入示例。隔离 wheel 验收要求 `app_cloud`、`apple_iap`、`cloud_kernel`、旧 `cloud_webhooks` 和产品包缺席，公共配置、注册和三类来源仍能通过测试。

## App Store 评论定时通知

`dwy_webhooks.reviews` 提供主动采集能力，独立于审核/构建 Webhook 和内购通知。评论通知安装 `dwy-webhooks[discord,reviews]`：`reviews` 直接声明 HTTPX、PyJWT 和 cryptography，使用账号 API 密钥签发 ES256 JWT 并访问 ASC REST API；不需要 Apple Server SDK 或 Resend SDK，也不依赖其它包偶然传入 PyJWT。无需 Redis 服务、ARQ Worker 或新增调度框架。

```bash
uv add 'dwy-webhooks[discord,reviews]==0.2.0'
```

```python
from sqlalchemy import MetaData
from dwy_webhooks.reviews import AppleReviewsConfig, build_review_tables, install_review_monitor

# project_settings、EAPI 创建的 sessions 及 app 都由消费项目提供。
config = AppleReviewsConfig(
    apps=project_settings.review_apps,
    issuer_id=project_settings.apple_issuer_id,
    key_id=project_settings.apple_key_id,
    private_key=project_settings.apple_private_key,
    discord_webhook_url=project_settings.review_discord_webhook_url,
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

新增源码不表示该版本已发布；消费项目必须安装包含 `dwy_webhooks.reviews` 的本轮 wheel，不能用旧 registry wheel 或源码路径替代制品验收。
