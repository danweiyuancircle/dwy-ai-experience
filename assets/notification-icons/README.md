# 共享通知图标

微信支付、Apple 通知、监控告警等场景共用的静态素材入口，不依赖 Python、Vue 或其他运行时。新增项目从此目录复用，不再分别设计渠道专属的同类图标。

| 名称 | 图形 | 用途 | 底色 | 预览 |
| --- | --- | --- | --- | --- |
| purchase | shopping-bag | 付款成功、买断购买 | `#0f766e` | ![购买](purchase.png) |
| subscription | repeat-2 | 首次订阅、重新订阅、立即升级 | `#0f766e` | ![订阅](subscription.png) |
| renewal | refresh-cw | 自动续订成功、扣款恢复后续订成功 | `#0f766e` | ![续订](renewal.png) |
| refund | undo-2 | 已确认退款 | `#b91c1c` | ![退款](refund.png) |
| alert | triangle-alert | 监控告警、退款待人工核对 | `#b45309` | ![告警](alert.png) |
| review | clipboard-check | 应用审核、版本状态 | `#2563eb` | ![审核](review.png) |
| report | 柱状图 | 经营日报、周报 | `#7c3aed` | ![报表](report.png) |
| email | mail | 邮件事件 | `#d97706` | ![邮件](email.png) |
| general | bell | 普通系统通知、内购动态 | `#475569` | ![通知](general.png) |

## 复用

- 每类同时提供可编辑的 `.svg` 和可直接使用的 `.png`，文件名保持一致。直接复制所需 PNG 到应用静态资源，或由自己的 HTTPS 静态站点托管。
- 需要公网头像时，使用可公开访问、不带鉴权、不会过期的 HTTPS 图片地址；发布到本仓库后也可使用固定提交 SHA 的 raw 文件地址。当前工作区新增素材未经提交、推送前没有公网地址，不使用浮动分支 URL。
- Discord 的 `avatar_url` 可使用托管后的 PNG；企业微信当前纯文本发送适配不读取头像字段，需在机器人支持的配置入口设置头像，不能靠替换素材让文字消息自动带图。
- 图标只表达通知类别，业务来源和处理结果仍用名称、标题及正文说明；告警不等同于已失败，退款不等同于付款成功。

## 维护规格

- 使用现有 Lucide 0.468.0，固定上游提交 [`f12b0de177fbc2a6795e99be065887e72b237123`](https://github.com/lucide-icons/lucide/tree/f12b0de177fbc2a6795e99be065887e72b237123/icons)。随素材复制或分发同目录 `LICENSE.lucide.txt`。
- 画布 `256 × 256`、背景圆角 `48`；原始 `24 × 24` 图形使用 `translate(56 56) scale(6)`，白色线框宽 `1.8`，圆线帽和圆连接。保留外围留白，适应圆形头像裁切。
- 修改 SVG 后同步导出同名 PNG，保持 `256 × 256` 和透明圆角；现有 PNG 使用 macOS AppKit 原尺寸栅格化，不截图、不引入图片生成流程。验收时检查小尺寸辨识度及圆形裁切。
- 此目录是后续维护入口。`backend/packages/webhooks/assets/` 与 `backend/packages/apple-notify/src/dwy_apple_notify/assets/` 保留历史兼容快照，已有固定提交或包标签引用不改动；新增使用此目录，不在历史目录继续扩充。
