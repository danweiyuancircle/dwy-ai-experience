# dwy-webhooks

## 0.4.0

- 新增公开 `dwy_webhooks.apple`：安全购买/续订详情、已验签 SDK 字段映射和可注入应用品牌的 Apple Discord 文案。
- 通用 Apple 路由展示金额/币种、店面、时间、购买归属、退款申请/退款结果分类及续订设置；缺失、零值和未知分类保持准确。
- 保留既有八字段构造、`public_data` 白名单和验签并发/关闭合同；不包含账户 token、原始 JWS 或业务权益规则。
- PyPI 仅上传通用 wheel；内部仍构建源码包用于归档与安装检查，不上传源码包。

## 0.3.0

- 同步实际项目验收后的评分通知样式，明确区分监控启用、新增和更新，并展示可视星级。
- Discord 发送者默认使用「Apple 应用通知」，支持低层发送器、全局来源配置和评分配置覆写；来源名称优先于全局名称。
- 名称在配置和发送边界统一校验；保持外部会话、迁移、凭据注入及原有调度与保留期行为。

## 0.2.0

- 新增 `dwy_webhooks.reviews`：通过 App Store Connect API 主动读取文字评论及星级，把新评论和内容修改投递到 Discord，不提供纯星级事件或 Discord 内回复。
- 新增独立 `reviews` extra，直接声明 HTTPX、PyJWT 与 cryptography；评论通知使用 `dwy-webhooks[discord,reviews]`，无需 Apple Server SDK 或 Resend SDK。
- 配置、签名密钥、应用清单、数据库会话、迁移表、客户端与发送器均支持宿主注入。每次完整分页成功后，在同一事务中提交评论、基线与通知 outbox。
- 默认每小时轮询，调度计划和 CAS 租约持久化，重启保留计划；FastAPI 生命周期停止后台任务后才释放宿主资源。
- 首次建立历史基线并发送单条摘要；后续内容变化支持幂等记录和失败重试。默认保留 30 天，允许 1–3650 天；扩大保留期静默补历史，过期评论与投递载荷会清理。
- 单轮最多 100 页、每页 200 条，每页响应不超过 2 MiB；超限或任一页失败均不提交部分基线。当前仍遍历全历史，保留期控制数据库内容而非 Apple 拉取范围。
- Discord User-Agent 同步为 `dwy-webhooks/0.2.0`。

## 0.1.1

- 首个公开 PyPI 版本，通过 GitHub Actions OIDC 发布。
- 显式声明 Ruff 的本包模块分类，使仓库根目录与包目录运行的导入排序检查一致。
- Discord 请求的 User-Agent 版本同步为 `0.1.1`；验签、注入与发送行为保持不变。

## 0.1.0（未公开）

- 首次通过 GitHub Actions OIDC 发布到公开 PyPI，导入命名空间为 `dwy_webhooks`，基础依赖为 `dwyeapi==0.12.0`。
- 提供公开配置、FastAPI 注册入口、中立事件与可替换接收器；密钥、路由、目标地址和存储资源由调用项目注入。
- 将 Discord 发送、Resend 事件、App Store Connect HMAC 和 Apple Server Notifications V2 适配为可复用模块，包含验签、去重、失败语义和发送边界。
- `discord`、`resend`、`apple` SDK 分别通过 extras 安装；基础安装及公开入口导入不要求这些平台 SDK。
