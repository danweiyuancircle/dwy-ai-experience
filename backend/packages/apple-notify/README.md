# dwy-apple-notify

Apple 通知集成：购买通知验签与文案、App Store Connect 审核事件、评论监控、经营日报和周报。通知投递统一使用 `dwy-notify`；本包不处理应用账户与权益。

## 按需安装

```bash
pip install 'dwy-apple-notify[iap,asc,reviews,analytics]==0.1.0'
```

`iap` 安装 Apple Server SDK；`asc`、`reviews`、`analytics` 分别安装现有 ASC HTTP/JWT/加密依赖。只使用审核、评论或报表时不需要 Apple Server SDK，也不需要 Resend。

## 模块入口

- `dwy_apple_notify.apple`：已验签通知与交易模型、购买文案。
- `dwy_apple_notify.config`：`AppleNotifyConfig`、各 Apple 来源配置。
- `dwy_apple_notify.fastapi`：`install_apple_notifications`、`AppleNotifySinks`、`AppleNotifyRuntime`。
- `dwy_apple_notify.analytics`：官方报表客户端、快照、存储与 monitor。
- `dwy_apple_notify.reviews`：评论客户端、存储与 monitor。

配置由宿主显式注入，本包不读取环境变量、不建数据库、不执行迁移。数据库会话、表和生命周期由宿主管理，已有队列表名、来源标识与目标指纹保持兼容。

## 经营统计日期

默认北京时间 `Asia/Shanghai` 每天 08:30，内部固定查询统计时区日期的前两天，例如 30 日查询 28 日、31 日查询 29 日。Apple 报表生成存在延迟，因此不暴露 `lag_days` 配置。周一附加截至前两天的连续七天周报。未生成的指标保留待发布状态，不把缺失数据写成零，不自动重复补发历史日报。

## 名称与头像

购买默认“购买通知”，审核默认“应用审核通知”，日报周报默认“经营报表”，评论默认“系统通知”。各模块 `appearance.py` 公开 `DEFAULT_APPEARANCE`；应用与单次发送可逐字段覆盖，最终名称必填，头像可省略或显式清除以使用平台默认。

Logo 沿用 GitHub 固定资产提交 `091ad4fea18ed3840fec83dc833f18b759256ca7`，无需应用部署图片服务。资产与 Lucide 许可维护于 `backend/packages/webhooks/assets/`，固定历史引用不受本次 Python 包迁移影响。
