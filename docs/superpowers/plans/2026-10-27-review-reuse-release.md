# 评分复用与可覆写 Discord 发送者实施计划

> Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 App Cloud 已验收的评分样式回灌 dwy-webhooks，新增可注入的默认发送者名称，发布 0.3.0 并让 App Cloud 改用正式包。

**Spec:** 用户已确认评分功能抽回共享库、验证后发布 PyPI、业务项目回接并部署；默认名称为「Apple 应用通知」，允许外部覆写。

**Architecture:** 复用现有 reviews 模块，保持数据库会话、迁移和凭据由调用方提供。DiscordWebhookSender 提供 username；WebhookConfig 提供全局名称，各来源配置可覆写；AppleReviewsConfig 提供评分名称。App Cloud 保留管理库表绑定与迁移，删除本地重复实现。

**Constraints:** 不修改其他共享包；不升级第三方依赖；仅通过现有 GitHub Actions OIDC 发布；源仓库保持私有；不重置现网基线或表数据；邮件显式注入独立名称。

- [x] 迁入评分样式测试，新增发送者默认/覆写/无效输入与高层配置透传测试，先观察失败。
- [x] 实现通用名称校验、传输与来源配置透传，回灌评分样式，更新文档和 TEST_CASES。
- [ ] 同步包版本、CI 内部引用、User-Agent 和 changelog 至 0.3.0；运行共享包测试、lint、安全检查与隔离 wheel 验收。
- [ ] 提交推送、打 dwy-webhooks@0.3.0 tag，监控 OIDC 发布并确认正式 PyPI 安装可用。
- [ ] App Cloud 使用 dwy-webhooks[discord,resend,apple,reviews]==0.3.0，删除重复评分实现与测试，保留宿主集成测试、表绑定和迁移。
- [ ] 完成业务项目源码与安装验收，再部署；验证共享源码路径、现有七应用基线、默认及自定义发送者实际消息。

## Review focus

- 默认、全局覆写、来源覆写及评分配置都应实际进入 HTTP JSON 的 username 字段。
- 直接发送器的名称校验错误不回显输入；配置模型沿用 Pydantic 的错误展示，不引入 dotenv 或宿主依赖。
- 新 wheel 的最小 reviews extra 能独立使用；业务集成从正式 PyPI 安装。
- 迁移 revision 和既有表名不变；重建容器不重复发送基线。
- App Cloud 的邮件通知必须覆写名称，保持邮件场景清晰。
