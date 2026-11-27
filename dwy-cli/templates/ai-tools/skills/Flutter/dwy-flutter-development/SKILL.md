---
name: dwy-flutter-development
description: 开发、测试、排查、评审或适配 Flutter 应用、Widget、UI 主题、导航与目标平台时使用。
---

# Flutter 开发

## 开始前：必须使用官方 Skill

开发前必须同时核对官方 Skill、可用 MCP、CLI 与实际 SDK，按下方工具路由执行；不能只读 Skill 就跳过其余三项。Flutter 的 iOS/Android 宿主还要核对 Xcode/Android SDK、项目最低版本和实际目标设备/runtime。

每项 Flutter 开发必须先读取并应用匹配的 [Flutter 官方 Skills](https://github.com/flutter/agent-plugins/tree/main/skills)，不能只读本文件、官方文档首页或工具介绍就算使用。纯 Dart 子任务同时读取匹配的 [Dart 官方 Skills](https://github.com/dart-lang/skills/tree/main/skills)。

优先读取已安装且来源可核实的官方 Skill；未安装时可直接读取官方仓库中的 `SKILL.md` 及任务所需引用文件，记录来源、适用工作流和实际执行结果。不自动安装整套插件、MCP 或全局工具。来源不可访问且无可用官方副本时，明确报告缺口，不把本地自编规范冒充官方 Skill，不宣称已完成官方工作流。

按 [官方工具与 Skill 路由](references/dwy-flutter-tooling.md) 选择具体入口。官方工作流决定如何开发、测试和诊断；下面资料补充团队和产品约束。用户已经选择的依赖不因官方示例使用另一库而被自动替换；安装与选版本仍遵循现有授权和依赖规则。

## 团队约束

- 团队新项目及首次封装的基础库从 Flutter 3.50.0 stable / 内置 Dart 3.14.0 起步，不保留旧版本下限、旧 UI 入口或兼容适配层。精确工具链、独立 UI 包与验证范围按 [基线与升级](references/dwy-flutter-ui-baseline.md) 核对；已有其他项目保留其锁定版本，未经任务授权不自动升级。
- 先核对 Flutter/Dart SDK、锁文件、宿主平台和已有实现。用官方 CLI 创建、分析、测试和运行；新宿主用 `flutter create` 生成，不手拼原生构建工程。
- 新移动项目默认 iOS 18+、Android 10+（`minSdk = 29`）；`targetSdk` 与最低版本分开核实。既有项目不因使用 Skill 被擅自升级；插件提高最低版本必须说明影响。
- 模块分层、依赖方向与抽取使用 `dwy-flutter-architecture`；Dart 语言、异步和纯 Dart 包使用 `dwy-dart-development`；消费 DWY 自有基础包使用 `dwy-flutter-appkit`，不要求每次加载全部入口。
- DWY 移动应用通过 `dwy_design` 的公开入口导入共享主题、组件与已导出的官方 Cupertino 控件，iOS 与 Android 共用页面和组件。把系统返回、键盘和安全区的适配集中在实际涉及的共用入口。
- **已采用 `dwy_design` 的应用，页面和业务组件必须直接使用它实际提供且满足需求的组件**（按钮、输入、搜索、设置分组、状态、确认、Sheet、玻璃页面骨架等）。禁止手写等价 UI 或再套同功能包装。页面级颜色、间距、圆角读取 `DwyTheme` / `DwyTokens`。只有核实共享组件缺失或确实无法满足需求时，才在项目 UI 层补具体缺口，优先组合共享组件。详见 [基础规范](references/dwy-flutter-core.md) 的“统一 UI 与适配”；其他自有基础能力同样按 `dwy-flutter-appkit` 的复用规则使用。
- 基础 Widget 从 Flutter 核心库导入。由直接使用独立 `cupertino_ui` 的共享库成员声明并管理版本。迁移时核对主题、国际化与第三方公开类型，仅在消费旧 SDK 控件时评估兼容桥。
- 先查共享包的真实接口、版本和验证状态；不能把待开发包当成已发布能力。无合适包时按已批准底座封装，不复制基础实现到产品。
- 不强制 Riverpod、Freezed、GoRouter 或某个 Mock 库。沿用项目已选方案，新依赖先选型；简单局部状态和简单模型可以用 SDK 能力。
- SDK 缺失、只有源码/静态检查、只有 Web 预览时，分别报告；不能宣称分析、测试、构建或移动端验收已通过。

## 按任务阅读

- 工具链、UI 迁移：[基线与升级](references/dwy-flutter-ui-baseline.md)
- 状态、生命周期、UI：[基础规范](references/dwy-flutter-core.md)
- 网络、异步与取消：按任务使用 `dwy-dart-development`
- 导航与深链：[路由](references/dwy-flutter-router.md)
- 单测、预览、真机：[验证](references/dwy-flutter-testing.md)
