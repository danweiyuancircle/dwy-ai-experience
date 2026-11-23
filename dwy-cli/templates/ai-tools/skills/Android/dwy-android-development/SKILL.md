---
name: dwy-android-development
description: 处理 Android 的工程配置、设备验证、系统适配和跨技术栈问题时使用。
---

# Android 通用开发

先检查项目现有语言、SDK、Gradle、依赖与设备目标。已有项目沿用当前依赖体系与 UI 框架。需要架构设计时同时使用可用的 `dwy-android-architecture`。

涉及具体代码时，按改动文件选用已启用的 `dwy-android-java`、`dwy-android-kotlin`、`dwy-android-xml` 或 `dwy-android-compose`。

- [开发规范与界面适配](references/dwy-android-core.md)：系统和设备适配按任务查阅；未启用专门 Skill 时，仍可查其中适用的存量语言、布局、资源和生命周期约定。AndroidAutoSize 是团队特定选型，新项目需先按依赖选型规则核实。
- [常见踩坑](references/dwy-android-pitfalls.md)：按工程、设备、界面或生命周期问题查阅。

涉及 UI、系统权限或设备行为时，区分编译通过和目标设备实际验证。

历史资料中的 `dwy-android-layering`、`dwy-android-mvp` 指 `dwy-android-architecture` 的对应参考资料，不是独立 Rule 或 Skill。
