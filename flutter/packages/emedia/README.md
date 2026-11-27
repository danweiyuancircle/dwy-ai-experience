# dwy_media

无自定义 UI 的移动媒体基础包，默认用于 iOS 18+、Android 10+（minSdk 29）。系统选择器、相机和 limited 授权管理仍由操作系统展示界面；本包不提供 Widget，也不是纯 Dart 包。

## 已批准底座

| 依赖 | 精确版本 | 来源与范围 | 许可 |
| --- | --- | --- | --- |
| `photo_manager` | `3.12.0` | FlutterCandies；相册、分页资产、缩略图、资源读取、有限授权 | Apache-2.0 |
| `image_picker` | `1.2.4` | Flutter 官方；系统选择、拍照、Android lost data | Apache-2.0 / BSD-3-Clause，按发行包文件声明保留 |

首次封装统一从 Flutter 3.50.0 / Dart 3.14.0 起步；不保留插件所允许的旧工具链下限。宿主和 workspace 统一解析依赖，不能通过 overrides 绕过冲突。当前已运行依赖解析与 9 项契约测试，平台验收边界见 `flutter/docs/foundation-3.50-validation.md`。

来源：[photo_manager](https://pub.dev/packages/photo_manager)、[版本页](https://pub.dev/packages/photo_manager/versions)、[image_picker](https://pub.dev/packages/image_picker)、[版本页](https://pub.dev/packages/image_picker/versions)。

## 能力与边界

- `DwyPhotoLibrary`：显式请求最小媒体范围权限、读取当前授权、列出相册、零起点分页、缩略图和打开资源。
- `DwySystemMediaPicker`：选单张/多张图片、选单个/多个图片或视频、拍照、启动时恢复 Android lost data。
- `DwyMediaFile`：只暴露名称、大小、字节流和读取，不暴露“永久路径”。名称来自外部系统，不应直接拼接成保存路径。
- 取消系统选择返回空列表，取消拍照返回 null；平台异常保留机器码和 cause，不假装取消或成功。
- 不删除/修改相册，不写相册、不申请音频、位置、麦克风或全部文件访问，不持有产品导航与会话。

## 使用

```dart
import 'package:dwy_media/dwy_media.dart';

Future<void> selectWithSystemPicker() async {
  final picker = DwySystemMediaPicker();
  final files = await picker.pickImages(multiple: true);
  for (final file in files) {
    final byteCount = await file.length();
    final stream = file.openRead();
    // 将 stream 与 byteCount 交给应用已有的传输/持久化入口。
    // 源资源仅在当前会话有效，不持久化源路径。
    await stream.drain<void>();
    assert(byteCount >= 0);
  }
}

Future<DwyMediaPage?> readPhotoPage() async {
  final library = DwyPhotoLibrary();
  var access = await library.permission(kind: DwyMediaKind.images);
  if (!access.canRead) {
    // 仅在用户点击进入相册功能后请求，不在应用启动时统一申请。
    access = await library.requestAccess(kind: DwyMediaKind.images);
  }
  if (!access.canRead) return null;
  final albums = await library.albums(kind: DwyMediaKind.images);
  if (albums.isEmpty) return null;
  return library.assets(albums.first, page: 0, size: 80);
}
```

`limited` 允许读取可见子集，不代表用户授予全部相册。当前选择可能只有视频，因此图片查询合法返回空。可在用户主动点击“管理可访问照片”后调用 `manageLimitedAccess(kind: ...)`，返回后重新读取权限和相册。

`albums` 的结果属于创建它的 `DwyPhotoLibrary` 实例。复用该实例分页；不要把相册元数据持久化后交给新实例。原生句柄在每个媒体范围重新列相册时更新，资源 ID 可能因删除/权限变化失效。`count` 是快照；`mayHaveMore` 只表示本页已满，可再请求一页，可能得到空页。相册发生增删时，页码式查询不能提供数据库快照一致性。

## 文件、iCloud 与恢复

`open(asset)` 可能下载 iCloud 原始资源，耗时和错误取决于系统网络与 iCloud 授权。资源不存在/未能取得文件时抛 `asset_unavailable`；缩略图不可用返回 null。包不会伪造文件、自动重试或调用全局 cancel-all。此首版未封装 iCloud 下载进度/原生取消，调用方应显示不确定加载状态；需要中断底层云下载时须进一步接入插件的逐请求能力。

读取返回的文件后，调用方负责复制到自己的持久目录或完成上传。`readAsBytes` 会分配整文件内存，大文件用 `openRead()`。本包不替应用选择覆盖路径，也不会擅自删除插件缓存；不要自行删除原相册资源。

在 Android 应用启动时、首次打开新的 picker 之前调用一次 `recoverLostData()`。该原生恢复是一次性的，返回后系统缓存会清除；应用应立即处理或可靠保存返回结果。其他平台默认无恢复结果。恢复错误抛出，不当作用户取消。调用方应串行启动系统 picker，避免插件报 `already_active`。

## 原生配置

本包不包含宿主工程，不擅自改应用权限。宿主必须通过官方 Flutter CLI 创建并配置：

- 最低 iOS 18、Android 10（minSdk 29）；compileSdk/targetSdk 依锁定 SDK 和插件要求分别核对。
- iOS：按实际使用添加相册/相机用途描述；不录像则无需为本包申请麦克风。默认 picker 使用 `requestFullMetadata: false`，避免仅选图片时额外索取完整相册元数据权限；仍按插件与 App Store 要求保留相册用途说明。
- Android：只用系统 picker 不预先申请 photo_manager 全库权限。自定义相册读取才按 images/videos 需求、API 分段声明所需媒体读取与 Android 14 limited 权限。不要添加全文件访问或定位权限；不得使用 `singleInstance` 启动模式。
- `photo_manager` 的 iOS limited 自动提示策略和宿主权限文案由应用决定；本包不关闭系统提示或权限检查。

精确配置以锁定插件文档为准，当前未生成宿主或做设备验证。HEIC、云端照片和 Android Activity 销毁必须真实设备检查，Web 预览不能证明通过。

## 测试与依赖隔离

`withAdapter` 构造器接收小型 DWY adapter，fake 测试无需创建相册页面或弹系统权限。本包仅输出 DWY 模型，不导出插件实体；具体插件实现位于 `lib/src/plugin_adapters.dart`，不属于稳定接入 API。

在 Flutter SDK 与 workspace 依赖解析完成后，在本包执行：

```bash
flutter analyze
flutter test
```

当前测试源码见 `TEST_CASES.md`，尚未执行；不要将 YAML/空白检查当作平台集成通过。

## 官方 Skill 工作流

已实际读取并应用：

- [flutter-apply-architecture-best-practices](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-apply-architecture-best-practices/SKILL.md)：先定义不可变模型，平台插件封装为 service，通过构造器注入测试 adapter；本任务无 UI/ViewModel，未添加空层、Freezed 或 DI 框架。
- [dart-add-unit-test](https://github.com/dart-lang/skills/blob/main/skills/dart-add-unit-test/SKILL.md)：测试放 `test/`、异步 `test/expect`、使用 fake 控制外部结果；包依赖 Flutter，故执行入口是 `flutter test`，不是 `dart test`。已使用 Flutter 3.50.0 运行，仍需原生设备验收。

第三方许可文本及归属由最终发行应用按各依赖的 LICENSE/NOTICE 纳入开源声明；本包暂 `publish_to: none`，未确定共享库发布许可证，不发布。
