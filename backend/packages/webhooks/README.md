# dwy-webhooks

基于 EAPI 的通用 Webhook 模块。接收 Resend、App Store Connect、Apple Server Notifications V2，并按项目配置转发到 Discord 或外部注入的业务接收函数。

## 安装与依赖

核心依赖固定兼容版本 `dwyeapi`；平台 SDK 按需选择 `dwy-webhooks[discord,resend,apple]`。ASC 使用标准库 HMAC；只有 Apple Server Notifications 需要 Apple SDK。源码由 dwy-shared 维护，项目安装独立 wheel，不引用共享仓库的绝对源码路径。发布配置不表示已经发布。

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
