# dwy-email-notify

## 0.1.0

- 从通用 Webhook 包独立 Resend 官方事件通知，保留原始载荷验签、事件筛选、来源标识和可配置路径。
- 邮件名称与固定 GitHub 头像由本模块预设，通知发送统一使用 dwy-notify，应用可覆盖名称或清除头像。
- Resend SDK 通过 resend extra 按需安装；支持自有持久化 sink，不包含业务发信、验证码和认证能力。
- 保持下游成功后确认、失败可重试和成功后去重语义，基础导入不依赖 Apple 或 Resend SDK。
