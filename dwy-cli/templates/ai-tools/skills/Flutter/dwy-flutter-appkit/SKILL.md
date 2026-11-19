---
name: dwy-flutter-appkit
description: 使用或排查 DWY 自有 Flutter、Dart 基础包、设计组件与平台适配包时使用。
---

# Flutter 自有基础包

先从项目 `pubspec.yaml`、`pubspec.lock` 和实际解析源码确认包名、来源与版本；版本范围不等于锁定版本。同仓 workspace 查当前源码，跨仓查已发布版本或明确 Git 提交，不以默认分支替代实际依赖。

- UI 主题、令牌和基础组件优先查 `dwy_design`；图片查 `dwy_image`；日志查 `dwy_log`；网络查 `dwy_network`。
- 偏好、安全存储、数据库和媒体分别查 `dwy_preferences`、`dwy_secure_storage`、`dwy_database`、`dwy_media`；内购查 `dwy_iap`，第三方登录查 `dwy_sign_in`，两者的凭据都必须由业务后端验证。这是模块查找入口，不是已发布或已验收清单。
- 在对应版本源码中读取包 README、公开入口、pubspec、测试与示例，确认初始化、生命周期、权限、错误处理和平台约束。缺少包或确切版本就报告缺口，不编造 API。
- 按需依赖，不建立强制引入全部能力的聚合入口。无 UI 的 Flutter 插件仍可能依赖引擎和原生配置，不能当作纯 Dart。
- 产品组合品牌和业务，复用基础件，不复制已有组件；产品 schema、DTO、账户策略留在产品。架构归属使用 `dwy-flutter-architecture`。
- 3.50 基线下分别核对 Flutter SDK 与独立 `material_ui` 的版本。公开 ThemeData、ColorScheme、组件主题等类型必须来自同一 UI 库；兼容桥不能转换新旧公开类型。迁移使用 `dwy-flutter-development` 并读取 [官方 UI 迁移说明](https://docs.flutter.dev/release/breaking-changes/material-ui-and-cupertino-ui)。
- 区分包声明下限、项目开发版本和实测范围。Gallery 或 Preview 的较高要求不自动成为所有包的最低要求；改包下限时追踪消费方。

团队仓库模块和示例从 `flutter/README.md`、`flutter/packages/<包名>/`、`flutter/examples/component_gallery/` 查找，以所用版本实际存在的内容为准。平台配置和设备验收配合 `dwy-flutter-development`，纯 Dart 行为配合 `dwy-dart-development`。
