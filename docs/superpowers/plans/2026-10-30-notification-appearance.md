# 通知展示实现计划

**Goal:** 在基础通知包提供可选展示参数，在 Webhook 模块提供可覆盖的分类预设与 GitHub 头像。

**Architecture:** dwy-notify 暴露 NotificationAppearance，控制平台参数但不识别业务；dwy-webhooks 各模块声明预设，统一队列与直接转发传递；App Cloud 的自有 IAP 队列调用公开预设。

**Tech Stack:** Python、Pydantic、现有 Apprise、pytest、公开 GitHub 静态 PNG。

**Spec:** docs/superpowers/specs/2026-10-30-notification-appearance-design.md

## 约束与审查重点

- 无新运行时依赖；保留既有日报前两天改动。
- 不修改目标 URL 或指纹；同目标线程锁内传递消息展示状态，不修改共享插件配置。
- 名称按层继承且发送前必须存在，显式 null 名称拒绝；头像可显式 null。拒绝非法名称及非 HTTPS/带账号密码的图片地址。
- GitHub 仅提交推送图标及许可；源码保持本地待发布，不触发包发布。
- 审查旧 URL 覆盖、无头像默认、并发串图、重试快照、其它渠道忽略不支持的展示参数。

## 步骤

- [x] 先补 notify 展示参数测试，验证失败，再实现 models.py、notifier.py、_plugins.py 的可选展示与平台默认。
- [x] 生成并检查各模块 Logo，提交推送独立资产，验证匿名公网 PNG。
- [x] 先补 Webhook 直接/持久发送与覆盖测试，验证失败，再增加各模块预设、统一发送传递及 App Cloud IAP 接入。
- [x] 跑两个包测试、受影响 App Cloud 集成测试、Ruff 与实际 wheel 独立验收；更新 README、测试清单与自审记录。

执行记录：直接在已有 develop 工作区串行完成；两个包及宿主接口有依赖，不派并行实现。仅图标托管需要 Git 提交推送；包发布与部署另行授权。

验证记录：notify/webhooks 合计 446 项通过；App Cloud 受影响 152 项通过；Ruff 与 diff --check 通过；实际 wheel 在独立环境的展示及经营烟测通过；五张 PNG 匿名 HTTP 200/image/png 且与本地产物一致。图标资产提交 091ad4fea18ed3840fec83dc833f18b759256ca7 已推送，源码未发布、未部署。

交付调整：新共享接口尚未发布，App Cloud 接入补丁改在独立源码副本验证并归档，真实工作区保持清洁。源码审查的 legacy 名称、显式头像及旧指纹三项问题均已修复并回归。生产日报旧去重状态需在后续部署时确认，当前不写生产状态。

追加用户约束已完成：发送者名称最终必填，头像可选；缺少名称在任何目标请求前拒绝，名称不可null，模块预设可满足必填。
