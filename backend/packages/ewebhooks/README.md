# dwy-webhooks（停止新增接入）

此包已拆分，新接入使用：

- `dwy-notify==0.2.1`：通用通知投递。
- `dwy-apple-notify[iap,asc,reviews,analytics]==0.1.0`：Apple 通知。
- `dwy-email-notify[resend]==0.1.0`：Resend 官方 Webhook 事件通知，不发送业务邮件。

以上为本轮目标版本，实际可用性以对应 GitHub Actions 发布结果及公共 PyPI 安装验收为准。迁移说明、当前入口与发布顺序见[通知包](../../../docs/notification-packages.md)。

历史 PyPI 版本和标签保留，不再为本次迁移发布旧包补丁。`assets/` 中的 PNG、SVG 与许可继续保留，已经使用的 GitHub 固定提交头像地址保持有效。迁移不清队列、不改变事件去重标识或目标指纹。
