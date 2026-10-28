# Apple 内购详情与 Discord 通知复用

用户明确要求把 App Cloud 0.1.3 的购买详情、退款原因及 Apple Discord 能力抽回共享库，独立发布并让业务项目回接。

保留现有 AppleNotificationVerifier 的官方验签、身份/交易关联核对及并发关闭规则。追加无账户 token、无原始 JWS、无权益策略的安全详情模型和 SDK 事实映射，既有 VerifiedAppleNotification 的八字段接口与 public_data 白名单保持兼容。通用文案接入现有 router，并通过公开 dwy_webhooks.apple 入口供已有业务队列直接调用；应用名称、Discord 目标和发送者名称由宿主提供。

App Cloud 的业务交易模型继承共享展示字段，保留账户归属、商品白名单、权益、独立 JSON 队列和申请退款不写权益的规则。宿主只做安全字段投影，不再维护金额、退款分类或文案副本。新旧业务 JSON 字段保持一致，上一版 0.1.3 可直接读取。

发布 dwy-webhooks 0.4.0，第三方版本不变；先源码测试和独立产物验收，再经 GitHub Actions OIDC 发布。沿用通用 wheel，本次只将 wheel 上传 PyPI，sdist 只用于内部产物检查。随后 App Cloud 固定新包、验证实际 wheel、发布正式修订版并部署。

- [x] 共享测试先失败：详情、零/缺失/未知原因、无业务敏感数据、品牌与发送者覆盖、旧接口、真实通用路由 HTTP JSON。
- [x] 抽出模型、映射和文案，保留现有验签实现；同步 README、测试清单、版本和 CI 引用（230 项及 lint 通过）。
- [ ] 源码/独立 wheel 检查，代码审查，经 OIDC 发布并确认 PyPI 只有通用 wheel。
- [ ] App Cloud 删除重复实现并回接正式包；验证旧 JSON、权益边界和三独立应用安装。
- [ ] 正式部署，复核已有真实 Apple 通知、旧数据连续性和公网版本，记录验收与回滚入口。
