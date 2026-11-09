# dwy-apple-notify

Apple 通知集成：购买通知验签与文案、App Store Connect 审核事件、评论监控、经营日报和周报。通知投递统一使用 `dwy-notify`；本包不处理应用账户与权益。

## 按需安装

```bash
pip install 'dwy-apple-notify[iap,asc,reviews,analytics,ratings]==0.1.8'
```

`iap` 安装 Apple Server SDK；`asc`、`reviews`、`analytics` 分别安装现有 ASC HTTP/JWT/加密依赖。只使用审核、评论或报表时不需要 Apple Server SDK，也不需要 Resend。

## 模块入口

- `dwy_apple_notify.apple`：已验签通知与交易模型、购买文案。
- `dwy_apple_notify.config`：`AppleNotifyConfig`、各 Apple 来源配置。
- `dwy_apple_notify.fastapi`：`install_apple_notifications`、`AppleNotifySinks`、`AppleNotifyRuntime`。
- `dwy_apple_notify.analytics`：官方报表客户端、快照、存储与 monitor。
- `dwy_apple_notify.reviews`：评论客户端、存储与 monitor。
- `dwy_apple_notify.ratings`：公开 Lookup 评分采集、独立每日调度、日周月变化与持久日报（当前源码新增，尚未发布）。

配置由宿主显式注入，本包不读取环境变量、不建数据库、不执行迁移。数据库会话、表和生命周期由宿主管理，已有队列表名、来源标识与目标指纹保持兼容。

`apple_original_platform(client, verify, transaction_id)` 使用 Apple 官方客户端查询 App 交易，并通过宿主提供的异步验签函数验证签名后返回平台。调用方负责超时和错误处理；可将结果传入 `VerifiedAppleNotification.original_platform` 显示。该平台表示首次获取 App 的平台，不能用于判断本次内购的设备，iOS 也不区分 iPhone 与 iPad。

## 购买通知图标（0.1.7）

`dwy_apple_notify.apple.apple_notification_appearance(notice)` 接收已验签通知，返回四类默认展示：订阅购买、买断购买、退款通知、内购动态。商品类型来自 `AppleTransactionDetails.product_type`（官方 Apple `type`）；不按商品名或有效期猜测。

购买要求生产环境、本人购买、金额大于零、交易编号／购买时间／币种齐全且未撤销，并且通知确实表达购买、续费或立即升级。非消耗型 `ONE_TIME_CHARGE` 才作为买断；共享、免费、Sandbox、缺字段、未知类型和普通状态更新使用通用图标。生产 `REFUND` 使用退款图标，申请／驳回／撤销退款仍为动态。购买不代表银行到账，退款保留正文中的原交易金额与归属。

默认 router 已将展示放进 `NotificationEvent.appearance`，配合 `dwy-notify 0.3.3` 的 relay 或 SQLAlchemy 队列传递并保存快照。宿主自有队列可直接调用该函数，把结果传给 `deliver_notifications(..., appearance=...)`；显式应用／URL 展示仍优先，重试沿用已有快照。

订阅和退款 SVG／256px PNG／Lucide 许可随 wheel 放在 `dwy_apple_notify/assets`。公网头像固定到 `dwy-apple-notify@0.1.7` 标签，正式发布时必须先公开该标签与资源；源码开发完成不代表头像地址已经可访问。买断购物袋与通用铃铛保留原固定提交地址。

## 经营统计日期

每个 `AppleAnalyticsConfig.apps` 条目可设置 `daily_report_enabled: false`：该应用仍按原计划静默采集并保存快照，只在指定时区的周一发送经营周报，不发送日报。默认 `true` 保持日报加周报，评分日报是独立配置，不受此开关影响。

默认北京时间 `Asia/Shanghai` 每天 08:30，内部固定查询统计时区日期的前两天，例如 30 日查询 28 日、31 日查询 29 日。Apple 报表生成存在延迟，因此不暴露 `lag_days` 配置。周一附加截至前两天的连续七天周报。日报和周报固定展示全部指标与地区、来源 Top 3：有值显示实际数值，获取不到显示“无数据”，真实零值保留为零。快照仍保留原始可用性状态，不把缺失数据写成零，不自动重复补发历史日报。

## 名称与头像

购买默认“购买通知”，审核默认“应用审核通知”，日报周报默认“经营报表”，评论默认“系统通知”。各模块 `appearance.py` 公开 `DEFAULT_APPEARANCE`；应用与单次发送可逐字段覆盖，最终名称必填，头像可省略或显式清除以使用平台默认。

Logo 沿用 GitHub 固定资产提交 `091ad4fea18ed3840fec83dc833f18b759256ca7`，无需应用部署图片服务。资产与 Lucide 许可维护于 `backend/packages/webhooks/assets/`，固定历史引用不受本次 Python 包迁移影响。

## 每日评分日报

从 `0.1.5` 起提供 `ratings` extra，仅使用现有固定版本 HTTPX；旧版 `0.1.4` 不包含该入口。开发时也可从仓库根安装源码：

```bash
pip install './backend/packages/apple-notify[ratings]'
```

宿主提供会话工厂、通知发送器和迁移，库不读取 `.env`、不创建数据库，不需要 Apple 账号或私钥：

```python
from dwy_apple_notify.ratings import (
    AppleRatingsConfig,
    RatingApp,
    build_rating_tables,
    install_rating_monitor,
)


def configure_ratings(app, sessions, metadata, sender):
    """宿主须先通过自身迁移创建 tables 对应的表，再启动应用。"""
    config = AppleRatingsConfig(
        apps={"1234567890": RatingApp(name="Demo")},
        territories=("cn", "us"),
        timezone="Asia/Shanghai",
        send_hour=8,
        send_minute=30,
        retention_days=90,
    )
    tables = build_rating_tables(metadata)
    return install_rating_monitor(app, config, sessions, tables, sender=sender)
```

也可配置 `notifications` 使用 `dwy-notify` 的已有目标。默认展示名称为“评分日报”。运行时位于 `app.state.dwy_rating_monitor`，公开 `monitor.run_once()` 与 `queue.process_pending()`；可注入 `client`、`sender` 和 `clock` 离线运行。采集器协议为 `async get_rating(app_id, territory) -> AppleRating(count=..., average=...)`，预期采集失败抛 `RatingCollectionError`；外部客户端由宿主关闭。

默认表为 `app_store_ratings_state`、`app_store_ratings_snapshots`、`app_store_ratings_deliveries`；`build_rating_tables(metadata, prefix=...)` 支持同库独立监控器。三表必须在同一数据库，保证有效租约下快照与 outbox 原子提交。库每分钟检查到期计划；每天只生成一份跨应用、地区日报，长文按 2000 UTF-16 单位无损分段。

读取地址为 `https://itunes.apple.com/lookup?id=1234567890&country=cn`，只使用 `userRatingCount` 与 `averageUserRating` 全版本字段。日/周基准分别为昨天和七天前，月基准为上月同日（月末截断）；按时区隔离历史，不跨地区相加。均分保留原始返回精度，展示累计均分之差；不足展示精度的非零变化明确标记，不伪造新增评分平均分。

缺失历史、基准日失败和当前采集失败分别展示；零值只来自有效零评分响应。当日采集失败也定稿日报，同日不再拉取；发送失败仅重试已生成内容。停机只采集当前已到期日期，不补造历史。历史默认保留 90 天，最少 32 天；切换时区不改写旧快照，已经生成的旧时区日报仍可投递。发送成功但本地确认前中断可能重复发送，不承诺严格一次投递。公开聚合数包含仅打星和文字评价附带的星级，无法识别逐条无文字评分。

每份日报的全部分段同时固定保存应用 ID 名单。投递前若发现其中任一应用已从当前配置撤销，整份日报标记为 `suppressed` 并清空内容，不重算或发送其中部分内容；完整停用后重新启用子集也执行此检查。只调整时区而未撤销应用时，旧时区待发日报仍正常投递。

采集跨过配置时区的午夜时，停止后续地区请求，整轮定稿为“采集跨日，本轮数据不可用”，包括丢弃午夜前已取得的部分成功值，避免把跨日数据写作昨日成功基线。失败快照的 `day` 为计划日期，`collected_at` 为实际失败完成时间；日报显示实际时间。计划日已完成后不重拉，次日仍按配置时刻执行。当前不保存逐项采集时间，需保留跨日部分成功值时再扩展该能力。
