# 通知模块分包与上线实施计划

**目标：** 发布 dwy-apple-notify、dwy-email-notify，集成 App Cloud 并发送生产验收测试通知；Apple analytics 固定统计发送时区日期前两天，不提供外部天数配置。

**已确认边界：** Apple 集成仅服务通知；email 仅接收邮件平台官方 Webhook 事件，不发业务邮件、不改验证码或认证。名称最终必填，头像可选，各通知模块持有自己的可覆盖预设。

**工作区：** 使用隔离 worktree，原仓库认证任务的未提交改动不进入本次发布。

## 接口合同

- notify 0.2.1 保留已有根 API，新增 `events.NotificationEvent`（保留原 source/scope/event_id/event_type/content/data 字段）与 `EventSink`。
- `dwy_notify.delivery` 提供 DeliveryPolicy、NotificationDeliveryError、deliver_notifications、delivery_failure；后者签名及 JSON payload 协议保持现有实现。
- `dwy_notify.sqlalchemy` 提供 build_delivery_table、SQLAlchemyDeliveryQueue，队列新增显式 appearance 参数，不再按来源查业务预设；表与租约字段保持原样。
- `dwy_notify.integration` 提供 NotificationSettings、configured_notifier、legacy_discord_config、delivery_error 和原有 URL/名称校验；兼容旧 URL 指纹及隐式名称优先级。
- `dwy_notify.relay` 提供 ReceiptStore、MemoryReceiptStore、NotificationRelay；relay 接收显式 appearance，不识别业务来源。
- 新领域包不得导入 dwy_webhooks；错误验签类型由各领域包持有。
- `dwy_apple_notify.config` 保留各 Apple 配置类名，聚合名 AppleNotifyConfig；`fastapi` 提供 AppleNotifyRuntime、AppleNotifySinks、install_apple_notifications。analytics/reviews 保持现有公开入口。各模块公开 DEFAULT_APPEARANCE。
- `dwy_email_notify.config` 提供 ResendWebhookConfig、EmailNotifyConfig；`fastapi.install_email_notifications` 只组合邮件事件路由。邮件模块公开 DEFAULT_APPEARANCE。
- 保留 source 字符串、Webhooks URL、表名、目标指纹与队列 payload，迁移不得清队列或倒退统计状态。

## 执行与验证

1. 基础层：从现有 webhooks 提取公共投递，先写新公开导入与通用队列测试并观察失败；迁移已有租约、部分重试、展示快照测试后通过 notify 检查。
2. Apple 包：迁移 Apple、ASC、reviews、analytics 源码与测试，按 iap/asc/reviews/analytics extras 声明已用 SDK；先验证新包导入失败再实现。固定前两天的跨月/跨年/08:30 回归，不接收 lag_days；检查新包无旧包依赖。
3. 邮件包：迁移 Resend 验签、事件筛选、通知文案和预设，按 resend extra 装 SDK；回归无效签名、重复事件及下游失败确认语义，无业务发信 API。
4. 主集成：维护新包 CI sources/锁文件与独立 OIDC workflow，构建 wheel/sdist 并执行归档检查、隔离安装和 SDK extras 隔离验收。旧 webhooks 历史发布不覆盖。
5. 发布：核对独立包版本、changelog、tag 和源码 SHA，依次发布 notify 0.2.1、领域包 0.1.0；新包先核实 PyPI 名称归属和 OIDC 发布配置，按已有 GitHub Actions 方式落地。
6. App Cloud：迁移全部 dwy_webhooks 导入及测试替身，安装正式 registry 包、冻结锁；运行已有 check-local.sh，审查精确 diff，保留现有独立应用与数据库边界。
7. 上线：核实运行容器与 Compose overlays、备份现有镜像/四库/配置；构建镜像、启动 PostgreSQL、迁移、重建 API，核实运行版本和实际包导入。
8. 验收：向已配置渠道发送购买、审核、报表、邮件、系统五类明确标记的测试通知，验证名称/头像及应用覆盖；测试不伪造真实 Apple 事件或改变权益。日报的真实历史状态切换单独审计，不以测试为由清库或重复补发。

## 分工

- 基础层执行者只编辑 backend/packages/notify。
- Apple 执行者只编辑新 backend/packages/apple-notify。
- 邮件执行者只编辑新 backend/packages/email-notify。
- 主执行者负责 CI、发布、App Cloud、审查、部署与最终验收；共同合同的变化先协调再修改。

每个执行者不提交、不发布、不触碰其它执行者目录，回报测试命令、结果和实际公开 API。
