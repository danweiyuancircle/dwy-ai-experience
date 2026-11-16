# dwy_secure_storage

Foundation 层的产品/账号安全存储。使用 `flutter_secure_storage` 的平台加密，不实现自己的密码学算法，不依赖 Widget 或页面。

```dart
import 'package:dwy_secure_storage/dwy_secure_storage.dart';

final secrets = DwySecureStorage(product: 'example-app', account: 'account-id');

Future<void> rememberSession(String token) async {
  await secrets.write('access-token', token);
}

Future<void> signOutLocally() async {
  // 宿主先停止该账号的请求、刷新及其他写操作。
  await secrets.clear();
}
```

作用域不可变，账号切换时建立新实例。前缀对每段分别编码；不会因 `a.b/c` 等分隔符碰撞串账号。`clear()` 读取插件键集合，只逐键删除本产品/账号前缀，绝不调用全局 `deleteAll()`。读取、写入及删除错误原样传播；清理非事务，部分删除失败时由上层明确处理，不显示退出清理成功。

Assembly 初始化 Flutter binding，并按插件文档配置平台。需要特定 Keychain accessibility、biometric 等策略时，注入已配置的 `FlutterSecureStorage` 实例；DWY 不默默扩大访问或开启生物识别。产品标识、账号标识与键的编码不提供保密能力；不要把秘密本身作为标识或写入日志。

## 平台要求与验证

共享移动端项目基线为 **iOS 18+、Android 10+（minSdk 29）**。该版本插件明确要求 Android API 23+，不高于项目 Android 基线；这不是已完成构建的证明，最终原生工具链与 entitlement 仍需统一解析后验收。依赖升级不得静默抬高基线。

Android 按插件要求排除不适合恢复的加密备份数据，避免恢复后无法解密。iOS 检查签名和 Keychain 配置；安全存储的卸载/备份行为由系统和插件决定，不承诺卸载即撤销凭据。

```bash
cd flutter/packages/dwy_secure_storage
flutter test
```

测试使用内存插件替身，证明作用域边界和失败传播，不证明Keychain/Keystore行为。已在Flutter3.50.0 / Dart3.14.0运行4项测试通过。真机需验证锁屏、重新启动、退出账号清理和升级；不触碰其他账号数据，见 `flutter/docs/foundation-3.50-validation.md`。

## 依赖

- `flutter_secure_storage` **11.2.0**，官方 pub API 首次发布时间 `2026-09-16T11:48:19.409417Z`。
- 发布者 Steen Bakker，社区库；BSD-3-Clause，可商用，消费应用须保留版权和许可声明，并纳入隐私协议的第三方开源组件附录。
- [版本](https://pub.dev/packages/flutter_secure_storage/versions/11.2.0)、[许可](https://pub.dev/packages/flutter_secure_storage/license)、[源码](https://github.com/mogol/flutter_secure_storage/tree/develop/flutter_secure_storage)。
