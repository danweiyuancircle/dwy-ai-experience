# dwy_preferences

Foundation 层的可选设置存储。基于 `SharedPreferencesAsync`，不维护 Dart 私有缓存，不依赖 Widget 或主题。

```dart
import 'package:dwy_preferences/dwy_preferences.dart';

final language = DwyPreferenceKey.string('language');
final settings = DwyPreferences(product: 'example-app');

Future<void> configure() async {
  await settings.write(language, 'zh');
  final savedLanguage = await settings.read(language); // String?，未设置为 null
  print(savedLanguage);
}
```

首次调用前由 Assembly 初始化 Flutter binding。`product` 与 `scope` 由宿主配置；编码后的命名空间保证分隔符不会造成碰撞。`clear()` 只清当前命名空间，使用插件 `allowList`，不删除原生代码或其他包的设置。

支持 bool、int、double、String、List<String>。同一名称必须始终使用同一类型，类型不匹配让插件抛错，不擅自返回默认值。字符串列表在读写边界复制，读取结果不可修改。修改后的语言、主题等如何通知 UI 属于上层状态管理。

此存储不保证业务级持久化提交，禁止存凭据、订单或重要业务记录。清理与写入不是原子事务，退出账号时由宿主先停写再清理。包中不创建产品单例。

共享移动端项目基线为 **iOS 18+、Android 10+（minSdk 29）**。依赖升级不得静默抬高基线；实际原生插件最低版本仍需依赖解析与构建核验。

## 验证

```bash
cd flutter/packages/epreferences
flutter test
```

测试使用注入的内存插件替身，只证明作用域和调用契约。已在Flutter3.50.0 / Dart3.14.0运行5项测试通过。真实平台写入、跨引擎读回和重启恢复需在iOS/Android单独验证，见 `flutter/docs/foundation-3.50-validation.md`。

## 依赖

- `shared_preferences` **2.5.6**，官方 pub API 首次发布时间 `2026-10-05T23:53:39.579508Z`。
- 发布者 Flutter 官方；BSD-3-Clause，可商用，消费应用须保留版权和许可声明，并纳入隐私协议的第三方开源组件附录。
- [版本与 API](https://pub.dev/packages/shared_preferences/versions/2.5.6)、[许可](https://pub.dev/packages/shared_preferences/license)、[源码](https://github.com/flutter/packages/tree/main/packages/shared_preferences/shared_preferences)。
- 声明的 Flutter/Dart 最低版本来自依赖元数据，不代表原生 OS 最低版本。实现包的最终 OS 要求须在统一依赖解析后核对。
