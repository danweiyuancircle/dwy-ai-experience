# 官方 CLI、Skills 与来源

本文件是官方工作流路由，不是官方 Skill 的副本。每项 Flutter 开发必须实际读取并使用匹配的官方 SKILL.md；不要仅凭名称、此表摘要或历史记忆宣称已使用。

## 开发前四项核对（必须）

| 类别 | 必须核对 |
| --- | --- |
| Skill | 官方发布来源、匹配任务的实际 SKILL.md 与必要引用、适用 SDK；记录采用步骤 |
| MCP | 本会话实际暴露的 Dart/Flutter、官方文档及相关原生平台工具，来源、连接状态、权限和能力边界；不能把配置存在视为已连接 |
| CLI | Flutter/Dart 与项目脚本的真实路径、版本、可用命令；移动宿主同时检查 Xcode/xcrun 或 Android SDK/ADB |
| SDK | Flutter/Dart 约束与锁文件、原生 SDK/插件要求、iOS deployment target、Android min/target/compile SDK、目标 runtime/架构 |

先核对现有能力；缺少或变化的部分再查官方说明。核对四类不等于必须安装或调用四类工具，匹配且已核实可用的官方能力直接复用。同一任务中版本、来源、权限、项目和目标未变可引用本轮证据，不能用旧历史快照当本次检查。

本轮先记录已找到/未安装/未连接/不适用/已使用；需要的验证无法执行时列为未完成。MCP 缺失可采用已可用的官方 CLI；实际 SDK 缺失时不能宣称分析、构建或原生运行通过。

## 官方来源

- [Flutter 官方 AI 工具说明](https://docs.flutter.dev/ai/tools)
- [Flutter team：flutter/agent-plugins](https://github.com/flutter/agent-plugins)
- [Dart team：dart-lang/skills](https://github.com/dart-lang/skills)
- [Flutter CLI](https://docs.flutter.dev/reference/flutter-cli)
- [Dart CLI](https://dart.dev/tools/dart-tool)
- [Dart/Flutter MCP 接入说明](https://docs.flutter.dev/ai/get-started)

仓库/Skill 会演进：核对来源和所用版本/提交。优先本机已经可用、可核实的副本；缺失时直接读取官方源文件及相关引用即可开展无需安装的指导工作。获取失败且无副本时报告官方 Skill 未能使用，不悄悄用本地说明顶替。

## 任务路由

| 任务 | 必须读取的匹配官方 Skill |
| --- | --- |
| 项目分层/共享边界 | [flutter-apply-architecture-best-practices](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-apply-architecture-best-practices/SKILL.md) |
| 响应式布局 | [flutter-build-responsive-layout](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-build-responsive-layout/SKILL.md) |
| Widget 测试 | [flutter-add-widget-test](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-add-widget-test/SKILL.md) |
| 组件预览 | [flutter-add-widget-preview](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-add-widget-preview/SKILL.md) |
| 真机/集成测试 | [flutter-add-integration-test](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-add-integration-test/SKILL.md) |
| 简单 JSON 模型 | [flutter-implement-json-serialization](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-implement-json-serialization/SKILL.md) |
| 深链/声明式路由 | [flutter-setup-declarative-routing](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-setup-declarative-routing/SKILL.md) |
| Dart 单测 | [dart-add-unit-test](https://github.com/dart-lang/skills/blob/main/skills/dart-add-unit-test/SKILL.md) |
| 依赖冲突 | [dart-resolve-package-conflicts](https://github.com/dart-lang/skills/blob/main/skills/dart-resolve-package-conflicts/SKILL.md) |
| 静态分析 | [dart-run-static-analysis](https://github.com/dart-lang/skills/blob/main/skills/dart-run-static-analysis/SKILL.md) |

不用一次读取全部。其他任务从官方目录选择匹配 Skill；Dart 基础包使用匹配 Dart Skill，并读取适用于 Flutter 集成的官方架构 Skill。官方示例中库的选择不覆盖用户已选底座，额外工具仍按权限与依赖规则处理。

## CLI 执行边界

先检查已安装环境；不会自动升级 SDK 或接受 Android/Xcode 许可：

```bash
flutter --version
dart --version
flutter doctor -v
flutter devices
```

根据当前任务与项目脚本执行，不机械跑所有命令：

```bash
flutter create --template=package dwy_example
flutter create --platforms=ios,android,web component_gallery
flutter pub get
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
dart test
flutter run -d DEVICE_ID
flutter build apk
flutter build ios --no-codesign
```

创建命令只用于新的目标路径；既有工程先检查差异，不覆盖手写宿主配置。纯 Dart 包用 `dart create --template=package`；Flutter 包/插件用对应官方模板。带 Flutter 成员的 workspace 用 Flutter 环境解析，数据库生成等命令在相应成员内执行。

禁止以 `flutter upgrade`、切 channel、`pub upgrade`、全局安装或清缓存当常规前置步骤；需要时先说明具体原因和授权范围。新工具安装按 dwy-tool-discovery，新增运行时依赖按依赖选型规则。不自动执行远程脚本或启用 MCP 的额外权限。

## 跟随 SDK 核对

- Material/Cupertino 的 SDK 入口与独立包、国际化及兼容桥按锁定 SDK 的官方迁移文档核对；不能把旧 import 当永久推荐，也不能只凭新文档批量迁移旧项目。
- Flutter 编译 iOS 时核对项目所选 Xcode/DEVELOPER_DIR 和实际 iOS SDK；Android 核对 SDK/JDK/Gradle 兼容范围。安装器或 doctor 提示不代表已经授权自动升级、接受许可或更改全局环境。
- Widget Preview 的命令、注解与平台限制用当前 SDK 验证，不将 Web 预览结果写成原生插件成功。
- 官方 MCP 已连接时优先使用适合的诊断、测试和运行工具；未连接时使用官方 CLI。找到 MCP/Skill 不等于已安装或已运行。
- 任务记录写明使用的官方 Skill、来源、应用到哪些步骤、实际命令和未完成项；不能用“按官方规范”代替证据。
