# dwy_iap

无界面的商店内购基础库：业务层面对统一的 `DwyBilling` 门面与模型，商店实现
（当前为 Flutter 官方 `in_app_purchase`，覆盖 App Store 与 Google Play）经
adapter 注入，未来接入其他商店技术时新增一个 adapter 即可。

## 边界

- 只封装客户端购买流程：查商品、购买、恢复、完成交付、凭据透传。
- **不做凭据验证**：`DwyPurchase.verificationData` 是平台原始凭据
  （iOS 收据/JWS、Android purchase token），必须由业务后端向商店验证后
  再发放权益；本库不发起验证请求，也不保存凭据。
- 只覆盖一次性买断商品（non-consumable）；订阅不在本期范围。
- 不定义 Widgets、不持有会员或额度状态、不请求商店以外的权限。

## 用法

```dart
final billing = DwyBilling();
if (!await billing.available()) return; // 隐藏购买入口

final products = await billing.products({'pro_lifetime'});
billing.updates.listen(_handlePurchase); // 持续监听购买与恢复结果

await billing.buy('pro_lifetime');
// 结果经 updates 流送达；status == purchased 时把 verificationData
// 交给业务后端验证，验证通过后调用：
await billing.complete(purchase);

final restored = await billing.restore(); // 恢复期间收到的 restored 购买
```

## 测试

```sh
flutter test
```

业务测试注入 Fake：`DwyBilling.withAdapter(fakeAdapter)`。
