# Flutter 开发基线

本文件集中维护当前工作区开发工具链；包的兼容范围仍以各自 pubspec 为准。升级经用户指定执行，不因模板刷新或新版本发布自动升级。

| 项目 | 当前基线 |
| --- | --- |
| Flutter | 3.50.0，官方 stable 正式标签 |
| Framework revision | ab2912035e160d9cad6306df307576da6128ebdb |
| 内置 Dart | 3.14.0；与 Flutter 同一工具链，不单独升级 |
| Engine revision | 371f77202a73e8dff57a8b3bff75bca55c090aee |
| Material UI | material_ui 1.11.0，复用升级前 pubspec.lock 已解析版本，改为 UI 成员直接声明 |
| 单测 | test 1.32.0，与该 SDK flutter_test 固定的 test_api 0.7.14 对齐 |
| 数据库代码生成 | build_runner 2.17.1 / analyzer 14.7.0，支持 Dart 3.14；不升级 Drift 运行时 |
| 移动目标 | iOS 18+ / Android 10+（minSdk29）；原生工程和插件仍须逐项核对 |

本机既有 PATH 工具链已原位升级，旧 SDK 另行完整备份；本机绝对路径不写入源码依赖。其他使用同一 PATH SDK 的项目会看到新版本，其依赖兼容性不能由本工作区结果代替。

开发前回读 `flutter --version --machine`，确认版本与 revision；`dart` 必须来自该 Flutter 工具链。CI 应使用同一精确版本，不使用浮动 channel。当前尚未配置 Flutter CI，不能声称已有持续集成保障。

本次为首次封装，全部包统一从 Dart 3.14 起步；依赖 Flutter 的包及 Gallery 同时声明 Flutter 3.50 下限。不支持更早版本，不保留旧 SDK Material 入口、兼容适配层或旧下限。纯 Dart 包不为版本声明引入 Flutter 依赖。

Material SDK 兼容导入迁移到 `package:material_ui/material_ui.dart`。调用方公开 ThemeData、ColorScheme、组件主题与回调类型须一起迁移；当前没有需要保留旧 Material 上下文的已确认依赖，不额外加入兼容桥。基础 UI 类型迁移属于消费方破坏性变更；包仍为 `publish_to: none`，本轮不发布。

来源：[SDK 标签源码](https://github.com/flutter/flutter/tree/3.50.0)、[官方迁移说明](https://docs.flutter.dev/release/breaking-changes/material-ui-and-cupertino-ui)、[material_ui](https://pub.dev/packages/material_ui/versions/1.11.0)、[test](https://pub.dev/packages/test/versions/1.32.0)。验证记录见 `flutter/docs/flutter-3.50-migration.md`。
