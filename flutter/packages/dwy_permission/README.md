# dwy_permission

无界面的 iOS / Android 运行时权限。默认用于 iOS 18+、Android 10+（minSdk 29）。本包不提供 Widget，也不在应用启动时申请权限。

## 已批准底座

| 依赖 | 精确版本 | 来源与范围 | 许可 |
| --- | --- | --- | --- |
| `permission_handler` | `13.0.2` | Baseflow；查询、请求、打开系统设置。发布于 2026-09-04 | MIT，商用闭源可用，强制署名 |

不包含鸿蒙、macOS、Web、Windows。相册枚举与系统选择器仍走 `dwy_media`，不要用本包再要一次全库权限。

来源：[permission_handler](https://pub.dev/packages/permission_handler)、[13.0.2](https://pub.dev/packages/permission_handler/versions/13.0.2)。

## 能力与边界

- `status` 只读当前授权，不弹框。
- `request` 只在调用方明确调用时才可能弹系统框。启动时不要调。
- Android 13 起 `status` 不再返回 `permanentlyDenied`。该值只出现在 `request` 的结果。
- `shouldExplain` 只回答 Android 是否该先解释用途。文案由业务层写，本库不弹窗。
- `openSettings` 打开系统设置。返回后再读 `status`，不假设用户已经改授权。
- 平台异常收成 `DwyPermissionException`，`code` 保留插件错误码。

## 使用

```dart
import 'package:dwy_permission/dwy_permission.dart';

Future<void> enableCamera() async {
  final permissions = DwyPermissions();
  var access = await permissions.status(DwyPermissionKind.camera);
  if (!access.canUse && access.canAskAgain) {
    access = await permissions.request(DwyPermissionKind.camera);
  }
  if (access.canUse) return;
  if (!access.canAskAgain) {
    await permissions.openSettings();
  }
}
```

## 宿主配置

本包不改宿主工程。接入方必须：

- Android `compileSdk` 37。`permission_handler` 13.0.0 的破坏性变更。minSdk 仍按项目基线 29。
- 只声明实际使用的权限。iOS 未使用权限进包会被 App Store 以 `ITMS-90683` 拒。
- iOS 缺用途文案时，查询或请求该权限会让进程退出。

第三方许可由最终发行应用按 LICENSE 写入隐私协议附录。本包 `publish_to: none`，不发布。

## 测试

在 workspace 依赖解析完成后，于本包目录执行：

```bash
flutter analyze
flutter test
```
