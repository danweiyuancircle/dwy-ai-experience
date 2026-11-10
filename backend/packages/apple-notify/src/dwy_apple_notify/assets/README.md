# Apple IAP 通知新增头像

本目录保留随 Apple 包分发的兼容快照；后续新增项目统一从仓库根 `assets/notification-icons/` 复用，见[共享图标说明](../../../../../../assets/notification-icons/README.md)。现有包标签和头像地址不改动。

- `subscription.svg`／`subscription.png`：订阅购买，Lucide repeat-2，底色 #0f766e。
- `refund.svg`／`refund.png`：已退款，Lucide undo-2，底色 #b91c1c。

沿用既有通知图标规格：256 × 256，圆角 48，图形原始 24 × 24，平移 56 后放大 6 倍，白色线框宽 1.8。PNG 由 macOS AppKit 从 SVG 原尺寸绘制，透明圆角保留。Discord 圆形头像裁切后主体处于安全区域内。

图形来自 Lucide 0.468.0，固定上游提交 https://github.com/lucide-icons/lucide/tree/f12b0de177fbc2a6795e99be065887e72b237123/icons ，保留同目录 `LICENSE.lucide.txt`。未新增运行时依赖。买断与通用图标复用原 `backend/packages/webhooks/assets/purchase.png` 与 `general.png` 固定提交地址。

资源随 Apple 包源码和 wheel 分发；默认公网 URL 固定到下一版 `dwy-apple-notify@0.1.7` 标签，正式发布前尚不可用。发布时确认该标签公开、PNG 返回成功且 Discord 实际可显示，不能以本地 PNG 验收替代。
