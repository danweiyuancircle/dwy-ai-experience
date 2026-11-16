---
name: dwy-flutter-architecture
description: 设计、开发、排查或评审 Flutter 模块架构、依赖方向、状态归属、共享基础库及代码抽取时使用。
---

# Flutter 架构

先读取 [Flutter 官方架构 Skill](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-apply-architecture-best-practices/SKILL.md) 及任务所需引用。官方 View/ViewModel、Repository/Service 描述对象职责，DWY 四层描述代码归属，不另套一份重叠目录。实际 SDK 与平台核对使用 `dwy-flutter-development`；来源不可用且无可核实副本时报告缺口。

- Assembly 装配；Features 承载功能；BizFoundation 保存产品内跨 Feature 的业务契约；Foundation 保存跨产品能力。
- Feature 不互引；跨域通过契约或 Assembly 协调。非 UI 业务层不依赖 Widget、BuildContext、主题和导航。
- 沿用项目选定的状态管理、DI 与 Repository 方案，不为四层创建空包，不引入万能全局 Store 或无业务价值的 UseCase。
- 抽取前确认是否跨产品复用；产品 DTO、数据库表和会话策略不自动进入基础库。消费接口与版本查 `dwy-flutter-appkit`。
- 提高共享包 SDK 或平台下限、迁移公开 UI 类型时先追踪消费方；不能用本机新版编译通过证明旧调用方兼容。

具体目录、依赖方向与 workspace 约束见 [四层与抽取](references/dwy-flutter-architecture.md)。Dart 代码使用 `dwy-dart-development`，Widget 与平台行为使用 `dwy-flutter-development`。
