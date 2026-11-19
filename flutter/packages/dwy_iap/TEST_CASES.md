# dwy_iap 测试用例

对应 `test/billing_test.dart`（门面契约，Fake adapter）与
`test/plugin_adapter_test.dart`（`InAppPurchaseAdapter` 映射与缓存，平台 Fake）；
真实商店弹窗、恢复时序由业务 App 真机验收覆盖，不在本包测试范围。

## 门面（billing_test.dart）

| 用例 | 验证点 |
| --- | --- |
| queries only products present in the store catalog | `products` 只返回商店目录内商品，未知 id 不报错、不返回 |
| buy forwards to adapter and results arrive via updates | `buy` 转发发起；购买结果（含凭据）经 `updates` 流送达 |
| restore returns restored purchases collected by the adapter | `restore` 返回恢复流程期间收到的 restored 购买 |
| complete forwards purchases to the adapter | `complete` 按购买转发给 adapter 记录 |
| wraps unexpected platform failures as store_error | 非 `DwyBillingException` 的异常被门面统一包装为 `store_error` |
| keeps DwyBillingException untouched | 本库异常原样透传，不被二次包装 |
| available reflects the store availability | `available` 如实反映商店可用性 |

## 平台适配（plugin_adapter_test.dart）

| 用例 | 验证点 |
| --- | --- |
| maps product details to catalog entries | 商品字段映射，`displayPrice` 取商店格式化价格 |
| product query error surfaces as store_error | 查询错误统一折叠为 `store_error` |
| buy reports a missing product as product_missing | 发起时商品不存在返回固定错误码 |
| buy reports a rejected purchase as purchase_rejected | 商店拒绝发起返回固定错误码 |
| purchase events map status and cache originals for completion | 状态映射、凭据取 server 侧、原始交易缓存；complete 后幂等，不重复 finish |
| restore collects restored purchases emitted by the stream | 恢复事件经流收集为列表，事件派发早于返回 |
