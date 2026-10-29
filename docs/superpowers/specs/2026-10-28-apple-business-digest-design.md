# Apple 经营日报与周报：dwy-webhooks 通用方案

状态：方案草案，尚未实现、发布或部署。核查日期：2026-10-28。

## 1. 目标与范围

为多个 Apple App 自动获取官方经营数据，通过 Discord 接收中文日报和周报，减少手动查看 App Store Connect。用户已明确公共能力放入 `dwy-webhooks`；本轮不包含管理网页。

推荐沿用现有 `dwy_webhooks.reviews` 的接入方式：公共包提供采集、统计、调度、持久状态和消息生成；调用项目注入配置、数据库会话、表定义与发送器，并拥有资源生命周期和迁移。App Cloud 是首个接入项目，不成为其他项目的运行依赖。

这是现有结构下最直接的方案。只放格式化函数会迫使每个项目重复采集与调度；把报表采集留在 App Cloud 则无法满足其他项目直接复用的要求。

第一版交付：官方可验证的下载、金额、订阅、地区与来源指标，日报、周报、失败提示和历史修正。需要额外身份或价格数据的派生指标另行验收，不用看似合理的比例替代官方口径。

## 2. 当前源码事实

以下来自当前本地 develop 源码，不代表线上版本：

| 位置 | 当前能力 | 本次处理 |
| --- | --- | --- |
| `backend/packages/webhooks/pyproject.toml` | 公共包版本 0.4.2；已有 discord/apple/reviews 等可选依赖 | 增加独立 analytics 能力入口，沿用已安装的 HTTPX、PyJWT、cryptography 版本；不引入新的基础设施 |
| `backend/packages/webhooks/src/dwy_webhooks/providers/apple_content.py` | Apple 交易与续订事件中文展示，区分取消自动续费和实际到期 | 保留独立实时事件；不把事件金额当开发者收益 |
| `backend/packages/webhooks/src/dwy_webhooks/reviews/client.py` | ASC ES256 认证、安全分页、有界读取 | 复用认证与同源分页规则；第二个使用方出现时只提取实际重复部分，保持现有评论错误码及行为 |
| `backend/packages/webhooks/src/dwy_webhooks/reviews/runtime.py` | FastAPI lifespan 安装、采集和队列运行、自有客户端关闭 | analytics 采用同一装配方式；不改评论的业务规则 |
| `backend/packages/webhooks/src/dwy_webhooks/delivery.py` | 表构造、持久去重、数据库租约、有界重试、429 退避 | 复用队列和表构造器，经营日报独立来源与投递表 |
| `backend/packages/webhooks/src/dwy_webhooks/discord.py` | 安全发送、禁 mentions、返回消息编号 | 继续使用；日报按完整行分段，避免截掉指标日期或币种 |
| App Cloud：`backend/src/app_cloud/reviews.py` | 向共享模块绑定管理库表定义 | 新增同等级 analytics 绑定，不向业务应用数据库写经营报表 |
| App Cloud：`backend/src/app_cloud/host.py` | 已调用共享 install_review_monitor | 新增经营报表安装；管理库初始化条件包含 analytics 启用状态 |
| App Cloud：`backend/pyproject.toml` | App Cloud 版本 0.1.5，固定依赖 dwy-webhooks 0.4.2 | 源码及实际 wheel 验收后再决定版本和依赖升级 |

当前没有发现经营报表采集模块。评论是带文字评论的星级数据，不等同于全部 App Store 星级评分；第一版只报告新增文字评论、低星评论等已采集事实，不宣称是商店完整评分总量。

## 3. 分析者应关注的指标

### 3.1 日报：规模、收入、订阅健康与变化

| 指标组 | 第一版展示 | 分析意义及边界 |
| --- | --- | --- |
| 下载 | 首次下载、重新下载、与前一日及上周同日比较 | 区分新增获客和回流；下载不是注册用户数 |
| 商店漏斗 | 独立设备曝光、产品页访问、商店曝光转下载率 | 官方转化率使用总下载及预购除以独立设备曝光；不能把产品页访问量当曝光分母 |
| 金额 | 销售额、开发者收益、退款金额，分别列币种 | 收益不等于最终到账；退款不能只凭负购买笔数识别，部分退款可能只有负金额 |
| 付费订阅存量 | 标准付费、付费优惠、免费试用分开，展示快照净变化 | 订阅数不等于去重付费人数；每日存量不能跨日相加 |
| 订阅流入 | 新增付费、优惠转正、续费分别计数 | 续费不是新增订阅；相同事件不能同时算两次 |
| 订阅流失与收款风险 | 主动流失、非主动流失、扣费异常及恢复；以官方实际事件分类为准 | 关闭自动续费不等于当日流失；宽限或重试期间不直接判定权益结束 |
| 试用 | 新开始、转正、结束计数 | 转化率需要成熟且匹配的分母；当日转正除以当日新试用不成立 |
| 地区与来源 | 下载与收益地区 Top 3、获客来源 Top 3，保留其他/未知 | 地区是 App Store 账户或店面口径，不是 GPS；不同来源报表不强行一对一对账 |
| 用户反馈 | 新增文字评论、1–2 星评论及更新提醒 | 复用现有评论模块的事实，评论均分不能冒充全部评分均分 |
| 数据健康 | 实际统计日期、完整度、延迟、连续采集失败 | 没有报表、未成熟、隐私隐藏、功能不适用和真实 0 分开 |

第一版金额优先采用 Analytics Purchases Standard 的销售额与收益字段；Sales Summary 作为后续商业总量核对来源，两套报表不相加。标准与详细报表的隐私规则不同，不能以详细报表的五人阈值认定标准购买报表也会隐藏小额收入。若隐私处理影响细分维度，地区或来源只显示可见部分并明确覆盖范围，不强制凑到总量 100%。

### 3.2 周报：回答增长来自哪里、是否可持续

- 同样长度、同样成熟度的连续七天比较：下载、销售额、收益、退款和订阅流入/流失。
- 地区、获客来源和订阅商品的贡献变化；统一为同一日期范围，缺失维度不推测。
- 订阅存量比较使用期末与期初快照，不累计七天存量。实际流入流出还可能涉及恢复、升级等，不强行用简单等式抹平官方差异。
- 低星评论及可复现问题清单；文字评论量不足时不据此推断全体用户满意度。
- 试用转正率、续费率、退款率只在分子分母和观察窗口经过官方报表验证后加入；第一版先交付对应计数与金额。

### 3.3 后续能力，不在第一版伪造数字

| 指标 | 价值 | 当前限制 |
| --- | --- | --- |
| MRR / ARR | 经常性收入规模 | Apple 页面有 MRR，但目前核查的 Subscription State 字段不足以直接导出；若自行计算，需处理价格、保留价、优惠、周期与币种；不能拿本月收入替代 |
| 下载后 D1/D7/D35 转付费 | 获客质量与付费速度 | Apple 页面有 cohort；公开 API 精确复现待核验。当天购买人数除当天下载不成立 |
| 每付费用户收益 | 付费深度 | Purchases 的 Paying Users 不可跨行或跨日直接求和；没有同范围去重分母就不计算 |
| D1/D7 留存、LTV | 长期产品价值 | 留存 cohort API 同口径待核验，LTV 需要充分观察历史；不能用短期收入外推并当事实 |
| 活跃设备、会话、崩溃、删除 | 产品质量与使用健康 | Apple 有部分使用报表，但只覆盖 opt-in，完整时间和阈值不同；应单列样本覆盖，周报后续接入 |
| CAC / ROAS / 关键功能漏斗 | 投放效率、产品路径 | 需要广告成本、自有埋点等额外来源，不是只靠 Apple 经营报表即可得到 |

## 4. 数据来源与获取流程

1. Analytics Reports API：发现或显式初始化 ONGOING 请求，枚举报表、实例和分片，下载 gzip TSV，校验并归一化。第一版优先标准报表，详细报表只在确有指标需求并说明隐私口径时使用。
2. Downloads、Discovery and Engagement、Pre-orders：下载与商店漏斗。曝光按唯一设备口径；缺少该分母或分母为 0 时比例显示不可计算，不显示 0%。
3. Purchases：购买类型、金额和来源维度。产品与退款分类按对应报告版本的字段规范解析。
4. Subscription State / Event：区分每日状态快照和当日生命周期事件。两类不混合累加。
5. Sales and Trends Summary Sales：后续可选核对，第一版不必为重复覆盖金额而强制增加此接口。接入时对单位、数量、币种、税费、负数和退款字段先用样本固定口径；不直接复用 Apple 通知的毫单位换算。它也不等同于最终到账财务报告。
6. Reviews：消费现有公共评论快照/汇总入口；不复制第二套评论采集器，也不跨模块读取私有存储实现。
7. 实时购买/续费/退款通知继续独立运行，只作事件提示，不回灌后再叠加日报官方报表金额。

Sales 和 Analytics 的统计日、处理时间与汇率口径可能不同；同比比较必须保持相同来源，不能为了填空在两套口径间无标记切换。

Analytics 首次请求需要 Admin 权限，后续下载可使用具备 Sales and Reports / Finance 等适当角色的密钥。初始化作为显式操作；常驻采集不为了初始化而一直持有额外高权限。评论密钥是否可同时用于报表须核查角色，不能因能读评论就认为报表也能读。

## 5. 公共模块边界

新增目录：`backend/packages/webhooks/src/dwy_webhooks/analytics/`。

建议从实际职责拆为 `models.py`、`client.py`、`metrics.py`、`formatting.py`、`storage.py`、`service.py`、`runtime.py` 与 `__init__.py`。不为每个指标建立一个类，也不新增通用插件框架。报表解析代码超出清晰规模时再按官方报表种类拆文件。

公共入口（设计名称）：

- `AppleAnalyticsConfig`：显式配置 API 凭据、App ID 白名单与显示名称、发送时区/时间、接收目标、历史保留时间。Vendor Number 只在以后接入销售报表时加入，不作为第一版必填项。
- `AppleAnalyticsClient`：初始化/发现报告、获取有界完整报告；可注入 HTTP 客户端；不读 `.env` 或项目设置。
- `AppleBusinessSnapshot`：明确类型的指标、金额和维度汇总；每项包含来源、统计日、状态与覆盖信息，缺失不补 0。
- `build_analytics_tables(metadata, prefix=...)`：仅声明表，不创建 engine、不执行迁移；同库多接入以账号 scope 与 App ID 隔离。
- `install_analytics_monitor(app, config, sessions, tables, *, client=None, sender=None)`：沿用 reviews 的显式装配；拥有采集、调度及投递后台任务，返回 runtime 便于执行一次采集或检查状态。
- `apple_business_digest_content(...)`：纯格式化；输入归一化数据，输出有界消息分段，可独立交给项目既有发送器。

其他项目只需配置、声明/迁移表并安装 monitor；无需复制 App Cloud 的 host、账户、商品权益或数据库工厂。普通 Python 项目也能直接使用 client、聚合与格式化组件，不强制安装 FastAPI monitor。

公共包不持有全局“当前 App”，不包含 ADBox/RightFlow 的硬编码名称，不代替项目维护商品权益，也不读取任意业务账本。

## 6. 调度、历史和投递语义

用户确认：Asia/Shanghai 每天 08:30，逐 App 一份日报；周一同一时间附加周报。第一版用 D-3 作为下载/订阅经营对比的共同统计日，避开不同报告两天/三天完整窗口的不一致。最新实时事件仍通过现有通知及时送达。发送时间与统计日时区是两件事，不能把发送时区当作对 Apple 聚合报表重新分桶的依据。

日报各区块明确日期与完整度；销售金额若展示更新的一天，必须单独标注日期且不与 D-3 的下载混算转化率。更保守的默认是整份主摘要对齐 D-3。

建议第一版默认保留 400 天归一化汇总与处理元数据，形成年度比较基础；不长期保存下载分片原文、签名 URL 或逐用户信息。单次采集预算和初始回补窗口明确有界，启动时不向 Discord 逐日补发历史。每天重查近七天实例及修正记录；更早历史修正提供手动范围回补入口，不承诺七天外自动完全覆盖。

状态表按账号、App 和任务持久调度租约；报告记录按实例/分片与处理日期去重；日期快照在修正后替换，不把实例修订当成又一份销售数据。全部必需分片成功后，才提交该报告版本的完整快照，失败保留旧版本并标记延迟。

快照提交与消息 outbox 写入使用同一事务。复用 `build_delivery_table` 和 `SQLAlchemyDeliveryQueue`，不能在快照提交后才单独调用会开启新事务的 enqueue 并留下丢消息窗口。复用现有表协议，不另写一套重试循环。

投递键由账号、App、日报/周报、期间、消息分段共同确定；重复运行不重复入队。已发送日报不随每次修正刷屏，修正进入历史和后续周报，必要时手动生成明确标记的更正消息。多段消息长度按 Discord UTF-16 限制检测，保留日期、币种和状态。

投递提供持久重试，仍存在 Discord 已接收但本地未确认时重发的窗口，不能承诺恰好一次。采集或发送异常使用稳定错误码，按 App 隔离；一个 App 失败不阻断其他 App。

初版只自动提醒权限失败、持续缺报和投递失败。收入/下载突降、退款率抬升等业务告警在有足够基线后再定阈值和最小样本，避免把小样本波动报成异常。

## 7. 安全与数据正确性

- API JWT 只发往固定 ASC API origin。Apple 提供的分片下载地址使用独立无 Authorization 请求，验证 HTTPS、地址来源及重定向规则；不能给下载域名继承 Bearer token，也不接受用户任意下载 URL。
- 限制分页、分片数、压缩响应体积、解压后总字节、行数、字段长度及请求时间；保护 gzip 解压和 CSV/TSV 解析边界。
- HTTP 错误、缺权限、报告未生成和无该产品能力各有可识别状态；隐私处理只有在来源足以确认时才标记，单纯缺行且无法判断原因时显示“数据不可用”，不能推断是隐私隐藏或真实 0。未知字段可兼容，缺失必需列或错误报表版本拒绝计算。
- 金额使用 Decimal；首版只展示 Purchases Standard 提供的 USD 估算值，不宣称取得顾客付款原币。后续原币核对不能将 USD/CNY/JPY 直接相加，换汇须记录来源与日期。
- 保留报表自身日期、粒度与 processingDate；多维计数只按该指标允许的维度聚合，不能跨行累计 Paying Users 或 Unique Devices 后冒充去重总数。
- 初始日报在可验证去重分母之前暂不输出跨细分总商店转化率；可用报表支持的同范围总量时才开启。明细来源份额不代表覆盖了所有用户。
- 存储只保留经营汇总和安全元数据；私钥、JWT、Webhook 地址、分片签名 URL、原始用户标识和原始错误响应不进入日志或消息。
- 新表通过项目 Alembic 创建。公共包只声明表，宿主管理库与各业务应用库及迁移继续独立。

## 8. App Cloud 接入范围

新增 App Cloud 宿主绑定模块 `backend/src/app_cloud/analytics.py`；配置进入 `backend/src/app_cloud/config.py`；装配进入 `backend/src/app_cloud/host.py`。本节路径均相对于 App Cloud 仓库根目录。

在 `backend/src/app_cloud/admin/migrations/` 新增管理库迁移，并注册 analytics metadata。更新后端依赖和配置示例；不把私钥写进示例。不修改客户端、各产品权益表或管理前端。

采集器的调度和表操作属于公共包；App Cloud 只提供配置、AdminRuntime.sessions、迁移和安装。以后其他项目使用自己的会话和迁移，不依赖 AdminRuntime。

## 9. 实施顺序与验收边界

1. 先取一个已授权 App 的脱敏标准报表样本，核对 App/商品映射、每项列定义、金额和日期口径、唯一设备聚合及缺数据语义；以后启用 Sales Summary 时再做跨来源金额核对。需要新增 ONGOING 时先显式初始化；首次生成约需 24–48 小时。
2. 先写失败测试，再实现客户端、标准报表解析与聚合。重点覆盖多分片重复/修正、缺列、下载失败、负金额但零笔数、混合币种、不可加总用户指标。
3. 接入快照、调度、日报/周报和现有 outbox。验证租约过期、并发实例、原子提交、重启、429、部分消息失败和历史回补不刷屏。
4. 第二个 ASC 客户端出现时提取最小共享认证/分页代码；跑现有评论、Apple 通知和 Discord 的受影响回归测试，保留原错误码与资源关闭语义。
5. 更新 `backend/packages/webhooks/tests/TEST_CASES.md`、公共 README 与不依赖 App Cloud 的最小示例。构建本轮 wheel，在没有 app_cloud/apple_iap/cloud_kernel 的新环境验收 analytics 独立安装、旧 extras 兼容和声明依赖完整性。
6. App Cloud 使用本轮实际 wheel 验收新增管理库迁移、host lifespan、关闭功能时无副作用、多 App 隔离及任务关闭。Python/uv 在 App Cloud 的 `backend/` 目录执行，隔离子进程必须使用当前环境解释器。
7. 报表 API 真实读取、Discord 实际收到预览、下一次定时执行、连续数日数据完整度是独立验收项；源码测试与 wheel 测试通过不等于这些项目已通过。
8. 发布与部署在另行确认的交付步骤执行。PyPI 走现有 GitHub Actions OIDC，App Cloud 仍按 Compose 构建、数据库、迁移、API 顺序。环境变更须重建容器，不能只 restart；本方案不执行发布。

## 10. 官方依据与待验证点

- [Analytics Reports API 目录、角色、初次生成及隐私处理](https://developer.apple.com/help/app-store-connect-analytics/overview/analytics-reports-api)：标准与详细报表区分；低量数据和噪声影响分析；不能把缺行当 0。
- [Analytics 隐私规则](https://developer.apple.com/documentation/analytics-reports/privacy)：Detailed 的阈值/噪声与 Usage 的最少样本规则，不能笼统套到 Purchases Standard。
- [Summary Sales Report](https://developer.apple.com/help/app-store-connect/reference/reporting/summary-sales-report)：可选销售核对字段；不能和 Analytics 相加，不能当最终到账。
- [App Store Downloads](https://developer.apple.com/documentation/analytics-reports/app-download)：首次/重新下载及完整窗口。
- [App Store Purchases](https://developer.apple.com/documentation/analytics-reports/app-store-purchase)：购买、金额、来源与 Paying Users 聚合限制。
- [Subscription State](https://developer.apple.com/documentation/analytics-reports/subscription-state)：状态快照及三天完整窗口。
- [Subscription Event](https://developer.apple.com/documentation/analytics-reports/subscription-event)：订阅生命周期事件。
- [Analytics 指标定义](https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions)：转化、MRR 等官方指标口径。
- [Download to Paid 等 cohort](https://developer.apple.com/help/app-store-connect-analytics/monetization/cohorts/)：按同批下载用户观察，不能用当日比值替代。
- [销售报表可用时间](https://developer.apple.com/help/app-store-connect/reference/reporting/sales-and-trends-reports-availability)：日报次日提供，和 Analytics 的日期/完整性分别处理。

尚需真实账号验证：报表初始化与下载权限、首份报告生成、可用平台与维度、Purchases 金额字段口径、唯一设备跨维度聚合、缺行/隐私边界与 App 商品映射。Sales 接入时再核对 Vendor Number。MRR、成熟 cohort 转化率、去重付费用户和全量留存不列为首版无条件承诺。
