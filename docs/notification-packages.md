# 通知包

通知能力按平台集成与通用投递分包。以下为本轮目标版本；发布流程尚需核对 GitHub Actions 结果与公共 PyPI，版本号不表示已经上传完成。

| 包 | 版本 | 职责 | 发布工作流 |
| --- | --- | --- | --- |
| `dwy-notify` | `0.2.1` | 通用通知投递、发送者展示与逐目标结果、可靠投递 | `.github/workflows/publish-notify.yml` |
| `dwy-apple-notify` | `0.1.0` | Apple 购买、审核、评论、日报与周报通知 | `.github/workflows/publish-apple-notify.yml` |
| `dwy-email-notify` | `0.1.0` | 邮件平台官方 Webhook 事件通知 | `.github/workflows/publish-email-notify.yml` |

## 安装与入口

```bash
python -m pip install 'dwy-notify==0.2.1'
python -m pip install 'dwy-apple-notify[iap,asc,reviews,analytics]==0.1.0'
python -m pip install 'dwy-email-notify[resend]==0.1.0'
```

Apple extras 可单独安装或组合：`iap` 提供购买通知验签，`asc` 提供审核事件与版本查询，`reviews` 提供评论监控，`analytics` 提供报表采集与摘要。只有 `iap` 需要 Apple Server SDK；审核、评论和报表不依赖邮件平台 SDK。

- 通用投递：`dwy_notify.Notifier`、`NotificationConfig`、`NotificationAppearance`；公共投递合同见 `dwy_notify.delivery`，SQLAlchemy 队列适配见 `dwy_notify.sqlalchemy`。
- Apple：`dwy_apple_notify.config`、`dwy_apple_notify.fastapi.install_apple_notifications`、`dwy_apple_notify.apple`、`dwy_apple_notify.reviews`、`dwy_apple_notify.analytics`。
- 邮件：`dwy_email_notify.config`、`dwy_email_notify.fastapi.install_email_notifications`；`resend` 是邮件平台 provider，不是业务发信模块。

邮件通知链路为“Resend 官方事件 → `dwy-email-notify` 验签与筛选 → 事件文案 → `dwy-notify` → 通知渠道”。它不发送业务邮件，不迁移 EAPI 发信、验证码或认证代码，回调 signing secret 与发信 API key 含义不同。

## 日期、名称与头像

Apple analytics 内部固定统计发送时区日期的前两天，默认北京时间 08:30 发送。例如 30 日统计 28 日，31 日统计 29 日；周一周报同样截至前两天。此延迟内聚在 Apple 模块，不提供 `lag_days` 等外部天数配置。未生成的指标保持待发布状态，不当作零，也不自动重复补发历史日报。

最终发送者名称必须由模块预设、应用配置、URL 显式配置或单次调用提供；合并后缺名会在发送前拒绝。头像可选，省略或显式清除时沿用平台默认，具体展示以渠道能力为准。

购买、审核、经营报表、邮件分别使用模块自己的名称与 Logo 预设，评论使用系统通知。应用可逐字段覆盖，单次调用优先于应用配置、URL 显式设置和模块默认。`dwy-notify` 不识别 Apple/Resend 业务来源，也不自带业务 Logo。

PNG 使用固定 GitHub 资产提交，示例：`https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/091ad4fea18ed3840fec83dc833f18b759256ca7/backend/packages/webhooks/assets/purchase.png`。历史资产与 Lucide 许可保留，应用无需部署图片服务；本次迁移不改写已有固定地址。

## 迁移与发布

新接入不再依赖 `dwy-webhooks`。旧包的历史 PyPI 版本与标签保留，不再为本次迁移发布旧包补丁。

迁移只改变 Python 归属和导入路径，保留原回调 URL、队列表名与字段、source、scope、event ID、目标指纹及已持久化的展示快照。不得清空旧队列、倒退统计状态或更换去重标识来完成迁移。应用账户、权益、数据库与事务仍由宿主持有。

先发布 `dwy-notify 0.2.1`，核实公共 PyPI 可安装后，再分别发布两个领域通知包。所有包使用独立版本、changelog、同名标签及 GitHub Actions OIDC；上传前检查实际 wheel/sdist 并隔离安装，部署只使用验收过的实际发布产物。

App Cloud 验收需覆盖购买、审核、报表、邮件、系统五种展示，测试消息明确标记为验收，不伪造真实购买或改变权益。源码测试、构建、公开包安装、生产部署和真实通知送达分别记录结果。

实施步骤见[本轮实施计划](superpowers/plans/2026-10-30-domain-notification-packages.md)，发布约束见[源码与公开包分发](private-distribution.md)。
