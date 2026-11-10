# 通知头像资源

本目录保留历史通知头像兼容快照；统一素材及新增告警图标改在仓库根 `assets/notification-icons/` 维护，见[共享图标说明](../../../../assets/notification-icons/README.md)。dwy-notify 不提供默认 Logo。PNG 用于 Discord 的公网 avatar_url，SVG 保留可编辑源。图形来自 Lucide 0.468.0，固定上游提交 f12b0de177fbc2a6795e99be065887e72b237123，保留同目录 LICENSE.lucide.txt。

- purchase：历史通用购买头像；新使用方按共享目录区分购买、订阅和退款
- review：应用审核与版本状态
- report：经营日报与周报
- email：邮件事件
- general：其它系统事件

默认公开地址固定到本仓库只包含资产的 Git 提交 SHA；已有资产 URL 保留。应用可覆盖为自己的 HTTPS 地址，不使用会过期的签名链接。
