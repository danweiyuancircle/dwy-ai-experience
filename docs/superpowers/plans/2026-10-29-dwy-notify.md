# 统一通知能力实施计划

> 用户已授权实施；直接在 develop 工作目录修改，不另建 worktree，不提交或发布。
> 本计划及本轮用户确认覆盖旧设计中的单目标、旧 SDK 独立路径和禁止复用 EAPI 的假设。

## 约定

- `dwyeapi` 是所有包可复用的基础能力与规范。新增 `backend/packages/notify/`，发行名 `dwy-notify`。
- 每个功能配置独立的 `notifications: NotificationConfig | None`；Webhook 全局可提供默认值，来源可覆盖。评论、日报各自配置，不依赖启用其他功能。
- `NotificationConfig.targets` 为目标名到 SecretStr Apprise URL 的映射；Notifier 只读取显式传入的配置。
- `Notifier(config)` 提供 `targets`、`target_fingerprint(name)` 和异步 `send(body, title="", targets=None)`。
- 结果 `NotificationResult.deliveries` 是 NotificationDelivery 元组；每条包含 target、success、message_id、error_code、retry_after、permanent；提供 success、succeeded、failed 汇总，不导出 SDK 类型。
- 所有默认发送统一走 dwy-notify；旧 Discord 入口仅转调，SDK 依赖删除。Apprise 支持的渠道可由配置选择，所有目标强制 TLS 校验、禁止重定向、禁用 SDK 重试和 optional 成功。
- 多目标队列状态写入现有 payload JSON，各目标独立记录结果与重试时间；成功后立即按租约 fencing 提交，避免整批重试。无需改变数据库表结构。旧内容载荷第一次处理时按当时配置初始化目标快照，后续不静默切换目标。

## 实施顺序

1. 先补通知包契约测试，验证失败，再实现 SDK 包装、企业微信业务错误校验、Discord mention 与限流安全边界；运行通知包测试及 Ruff。
2. 先补队列多目标、重启、租约、目标变更、部分永久失败测试，再实现 JSON 目标账本，保留旧 sender 注入和评论过期语义。
3. 更新 Webhook relay、各配置模型、评论与日报安装器；先补独立目标配置测试，再统一默认发送与兼容入口。
4. 同步 README、示例、TEST_CASES、CI 包清单／锁文件和 OIDC 发布工作流；新增普通 Python 通知用法与各来源不同目标示例。
5. 运行通知包与 Webhook 受影响全包测试、Ruff、独立 wheel 安装烟测；记录真实渠道投递尚未验收。不发布、不修改其他消费仓库。

## 验收

- Resend 发 Discord、Apple 内购发企业微信可同时配置；评论与日报独立配置多目标且按需启用。
- dwy-webhooks 不再导入 discord_webhook；旧发送 API 经 dwy-notify 仍返回真实 Discord ID。
- 多目标部分失败后仅重试失败目标；重启保留成功记录；目标变更不把既有通知发送到不同接收方。
- 错误码、429、超时、取消、日志秘密保护及现有隔离／生命周期不退化。
- 安装包不依赖源码路径，PyPI 发布仅通过 GitHub Actions OIDC。

## 本轮完成记录

- 已实现独立通知包、来源配置、统一兼容入口与原 JSON 载荷中的逐目标账本；未引入新数据库表。
- 已同步 README、来源分流示例、测试清单、CI 锁与 OIDC 发布工作流。
- 最终源码验证：通知包 48 项、Webhook 包 335 项测试通过，两个包及示例 Ruff 通过；冻结依赖同步与锁一致性检查通过，环境不再安装旧 Discord SDK。
- 最新 wheel 和 sdist 构建通过；使用两个隔离环境从实际 wheel 安装，Apple 与经营日报烟测通过。
- 独立代码审阅发现的 SDK 内部重试问题已修复并加入回归；不支持的协议在通知包 README 中明确列出。
- 未提交、推送、发布、配置 PyPI Trusted Publisher 或向真实 IM 外发；保留原有未跟踪的 Apple 日报设计文件。
