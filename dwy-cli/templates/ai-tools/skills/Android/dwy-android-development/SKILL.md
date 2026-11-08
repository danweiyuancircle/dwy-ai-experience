---
name: dwy-android-development
description: 开发、修改或排查 Android 原生应用时使用；覆盖 Java、Kotlin、XML、系统适配及常见问题。
---

# Android 开发

先检查项目现有语言、SDK、Gradle、依赖与设备目标；已有项目遵循实际技术栈，不擅自替换 Support、AndroidX 或 UI 框架。需要架构设计时同时使用可用的 `dwy-android-architecture`。

- [开发规范与界面适配](references/dwy-android-core.md)：按任务阅读语言、布局、资源和生命周期相关部分；其中 AndroidAutoSize 是团队特定选型，新项目也需按依赖选型规则核实，不能在未授权时自动添加。
- [Support 老项目兼容](references/dwy-android-support-only.md)：仅项目实际使用 Support 时阅读。
- [常见踩坑](references/dwy-android-pitfalls.md)：按工程、设备、界面或生命周期问题查阅。

涉及 UI、系统权限或设备行为时，区分编译通过和目标设备实际验证。

历史资料中的 `dwy-android-layering`、`dwy-android-mvp` 指 `dwy-android-architecture` 的对应参考资料，不是独立 Rule 或 Skill。
