# Changelog

## 0.1.0

- 新增 `DwyBilling` 门面与 `DwyBillingAdapter` 抽象；`InAppPurchaseAdapter`
  基于 Flutter 官方 `in_app_purchase` 3.3.1 覆盖 App Store 与 Google Play。
- 统一购买状态模型与固定错误码；凭据原文透传，验证由业务后端完成。
