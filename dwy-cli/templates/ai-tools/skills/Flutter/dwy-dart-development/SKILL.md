---
name: dwy-dart-development
description: 开发、排查或评审 Dart 代码、模型、异步逻辑、网络边界及纯 Dart 基础包时使用。
---

# Dart 开发

团队首次封装的共享基础库从 Dart 3.14.0 起步，对应 Flutter 3.50.0 stable；不保留更早版本兼容下限或适配层。纯 Dart 包不引入 Flutter 依赖。其他已有项目仍按自身锁定工具链开发，不自动升级。

先核对目标包的 `pubspec.yaml`、锁文件和实际 Dart 路径/版本，再读取任务匹配的 [Dart 官方 Skill](https://github.com/dart-lang/skills/tree/main/skills) 及必要引用。来源不可访问且无可核实副本时报告缺口，不能用团队规范代替官方工作流。

Flutter 工作区使用项目 Flutter SDK 内置的 Dart；独立 Dart 项目按自己的工具链。Flutter 工具链与平台核对使用 `dwy-flutter-development`，不会因使用本 Skill 自动升级已有项目。Dart 单测、静态分析及依赖冲突分别查官方目录的 `dart-add-unit-test`、`dart-run-static-analysis`、`dart-resolve-package-conflicts`，先实际读取再执行。

- 新语法和标准库 API 必须符合目标包的 SDK 下限，不能因本机 Dart 较新就直接采用。提高下限时核对调用方并同步声明、文档与验证；声明支持的下限没有实测时如实标记。
- 遵循 Effective Dart 和已有 analyzer 配置，公开 API 有类型，写清用途、返回语义及资源/取消约束；外部输入必须校验，内部类型契约不重复兜底。
- 简单局部模型与逻辑先用标准库；沿用已选依赖，不强制 Freezed、生成器或 Mock 库。生成代码由锁定版本的生成器产生，不手写冒充。
- 异步失败保留 cause/stack；订阅、文件、客户端由创建或明确接管的一方释放。取消不伪装为成功，不吞异常。
- 使用官方 CLI 或已核实官方 MCP 执行 format、analyze 和 Dart 单测；纯 Dart 测试通过不等于 Flutter 插件或设备验证通过。

编码、配置和输入边界见 [Dart 规范](references/dwy-flutter-core.md)；网络、取消、文件与日志见 [网络边界](references/dwy-flutter-network.md)。涉及 Widget 使用 `dwy-flutter-development`；调整模块边界使用 `dwy-flutter-architecture`；消费自有包使用 `dwy-flutter-appkit`。
