# 统一通知能力设计

本设计以 2026-10-29 用户确认及 `docs/superpowers/plans/2026-10-29-dwy-notify.md` 为准。新增 `backend/packages/notify/`，发行 `dwy-notify==0.1.0`；`dwy-webhooks` 升至 `0.6.0`。`dwyeapi` 是可复用的基础能力，通知包可依赖其配置和日志规范。

## 通知包合同

- `NotificationConfig(targets: dict[str, SecretStr], timeout_seconds=10)`：目标名称映射到 Apprise URL，只读显式参数，不读取环境、项目 settings 或证书文件。
- `Notifier(config)`：提供 `targets`、`target_fingerprint(name)` 及异步 `send(body, *, title="", targets=None)`；未传 targets 时发到全部配置目标。
- `NotificationResult.deliveries` 为不可变逐目标结果，包含 target、success、message_id、error_code、retry_after、permanent；`success` 为全部成功，`succeeded` / `failed` 为目标名元组。不导出 SDK 类型。
- Apprise 作为统一渠道 SDK；所有已支持的 HTTPS 渠道尽量通过配置使用，不限制为两个渠道；SMTP、本地命令、明文协议及无法禁用内部重试的插件在构造时拒绝。SDK 安全修正与异常适配集中在通知包，业务不写第二条 HTTP/SDK 发送路径。

Discord URL 示例为 `discord://Mail@WEBHOOK_ID/WEBHOOK_TOKEN`；企业微信机器人为 `wecombot://BOT_KEY`。完整 URL 是秘密，由宿主取得后传入，不放进日志、异常、队列载荷或文档实例值。

所有默认目标强制 TLS 校验，拒绝重定向，禁用 SDK 内部重试，不把 optional 目标失败记为成功。企业微信的 HTTP 200 仍校验业务错误码；Discord 禁用 mentions，安全处理消息编号与 429 延迟。错误只暴露稳定安全字段，不回显 token、原始响应或底层异常。取消继续传播；已开始的同步请求仍在线程中由 socket 超时结束，分段和多接收人通知不保证整条硬截止。普通渠道失败只返回 `send_failed`，插件日志隔离，不在发送内等待重试。

## 功能装配

`WebhookConfig.notifications` 是来源默认值。`ResendWebhookConfig`、`AppStoreConnectWebhookConfig`、`AppleNotificationsConfig` 的同名字段可覆盖默认值。`AppleReviewsConfig.notifications` 和 `AppleAnalyticsConfig.notifications` 各自独立。安装器按本功能配置创建 Notifier，不增加额外 notifier 注入要求。

因此同一项目可以让 Resend 发 Discord、Apple 内购发企业微信，评论发一个目标、经营日报同时发多个目标；每个功能单独安装、单独运行，不要求先启用另一个功能。自定义 Webhook sink 或评论/日报 sender 保持最高优先级。

旧 `discord_webhook_url`、`discord_username` 和公开 `DiscordWebhookSender` 入口保留兼容；旧入口内部转调通知包，仍返回真实 Discord 消息 ID。同一层同时配置新旧目标会被拒绝；来源配置仍可覆盖全局默认。旧 `discord` extra 保留为空，删除 `discord-webhook` SDK 依赖。

## 多目标持久队列

`SQLAlchemyDeliveryQueue` 接收旧 sender 或关键字 `notifier`，两者恰好一种。已有 sender 的返回和失败合同不变。通知模式将原 payload JSON 扩展为逐目标账本，记录名称、URL 指纹、状态、尝试次数、下次重试时间和结果；不新增表或修改 schema。

每个目标成功后立即按当前租约 fencing 提交；后续失败只重试尚未成功目标，重启也保留成功记录。目标永久失败不丢弃其它目标的成功事实。旧内容载荷在首次处理时绑定当时配置；已绑定目标被删除或 URL 指纹改变时安全终止对应投递，不静默转发到新接收方。凭据变化需要宿主明确决定旧任务如何处置。

保留评论过期清理、应用范围隔离、租约与旧 worker 栅栏、速率限制、资源所有权及取消语义。网络已投递但提交前进程中断仍存在重复窗口，不承诺恰好一次。

## 分发与验收

- CI 锁定通知包及 dev extras，跨包 CI 执行通知与 Webhook 全套合同测试及 Ruff。
- `.github/workflows/publish-notify.yml` 按包标签校验版本、构建、检查独立 wheel，然后通过 PyPI OIDC 上传通用 wheel。正式发布前先配置 Pending/Trusted Publisher；不使用长期 token。
- 先发布 `dwy-notify==0.1.0` 并验收公共依赖可安装，再发布 `dwy-webhooks==0.6.0`。本轮不提交、推送或发布。
- 独立 Apple/经营 wheel smoke 只 mock `dwy_notify._transport.post`，验证实际配置、业务格式化与持久队列；确认不安装 `discord_webhook` 或无关来源 SDK。
- README 与 `backend/packages/webhooks/examples/new_project/notifications.py` 展示来源分流、评论独立目标、日报多目标及普通 Python 使用方式。

源码测试、离线 HTTP 和 wheel smoke 不等于真实渠道投递；真实 Discord、企业微信及其它 Apprise 渠道分别验收。
