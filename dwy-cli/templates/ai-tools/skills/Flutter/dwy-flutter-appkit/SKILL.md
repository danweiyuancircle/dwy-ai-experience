---
name: dwy-flutter-appkit
description: 使用或排查 DWY 自有 Flutter、Dart 基础包、设计组件与平台适配包时使用。
---

# Flutter 自有基础包

## 先确认项目实际使用的代码

逐包核对声明范围、实际来源和源码，不把整套基础包当作同一版本。先读 [版本与源码定位](references/version-resolution.md)：覆盖 hosted、Git、path、workspace、依赖覆盖及解析产物不一致的情况。同名同版本也可能是不同代码；Skill 更新不代表项目依赖已经升级。

本 Skill 与引用资料提供能力导航和接入检查点，不是任意旧版本的 API 保证。调用方式以项目实际解析源码中的 README、`lib/` 公开入口、pubspec、测试和示例为准；当前主干或在线最新示例不能替代实际依赖。缺少能力时先评估现有 API，确需升级再说明目标版本、差异及验证范围，未经任务授权不改依赖或 SDK。

## 按任务读取资料

| 需求 | 基础包 | 按需资料 |
| --- | --- | --- |
| 主题、组件、图片 | `dwy_design`、`dwy_image` | [界面与图片](references/design-images.md) |
| 网络、日志、偏好、安全存储、数据库 | `dwy_network`、`dwy_log`、`dwy_preferences`、`dwy_secure_storage`、`dwy_database` | [数据与基础服务](references/data-services.md) |
| 第三方登录 | `dwy_sign_in` | [登录凭据](references/authentication.md) |
| 商店内购 | `dwy_iap` | [购买与恢复](references/purchases.md) |
| 运行时权限、相册、系统选择器 | `dwy_permission`、`dwy_media` | [权限与媒体](references/permissions-media.md) |

这里只列查找入口，不代表项目版本已包含这些包，也不是已发布或已验收清单。

## 共同约束

- 按需依赖，不建立强制引入全部能力的聚合入口。无 UI 的 Flutter 插件仍可能依赖引擎和原生配置，不能当作纯 Dart。
- 产品组合品牌和业务，复用基础件，不复制已有组件；产品 schema、DTO、账户策略留在产品。架构归属使用 `dwy-flutter-architecture`。
- Flutter 3.50 基线使用独立 `cupertino_ui` 与 `dwy_design` 统一 Android 和 iOS 的 Apple 风格。以实际版本的 `CupertinoThemeData`、公开入口和示例为准，UI 包版本与 SDK 分开核对。
- 区分包声明下限、项目开发版本和实测范围。Gallery 或 Preview 的较高要求不自动成为所有包的最低要求；改包下限时追踪消费方。

团队仓库模块和示例从 `flutter/README.md`、`flutter/packages/<包名>/`、`flutter/examples/component_gallery/` 查找，以所用版本实际存在的内容为准。平台配置和设备验收配合 `dwy-flutter-development`，纯 Dart 行为配合 `dwy-dart-development`。

## 维护基础包时

公开 API、初始化/生命周期、权限配置、平台或工具链下限变化时，同步检查本 Skill、相关引用资料和包 README；发布前按该包上一发布版本或提交对照实际差异，不假设所有包一起升版。只有发布历史可证明时才标注 API 的引入或移除版本；未发布内容不能标成已发布能力。此检查不授权更新消费者依赖、发布或修改全局已安装 Skills。
