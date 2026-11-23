---
name: dwy-android-support-only
description: 用于启用了仅 Android Support 约束的项目。修改源码、XML、Gradle 或第三方依赖时，保持 Android Support Library 体系，禁止引入 AndroidX。
---

# 仅使用 Android Support Library

在本 Skill 启用的项目中维持 Support Library 体系。先查看目标模块和构建变体的 Gradle 依赖、源码 import、XML 控件及主题配置。若已有 AndroidX 配置或依赖与约束冲突，说明具体位置，先明确维护还是迁移，再改动冲突部分。

- 兼容库依赖沿用项目已锁定的 Support 版本。Java、Kotlin、XML、Manifest 和混淆配置引用 Support 类时使用 `android.support.*`，禁止引入 `androidx.*` 或 AndroidX Material 组件。
- 确认当前工具链下 `android.useAndroidX` 和 `android.enableJetifier` 的实际值为 `false`。发现与约束不符的配置时，先核对受影响构建变体，避免仅改开关导致现有构建失败。
- 新增或更新依赖时，查目标变体的传递依赖，选用兼容 Support Library 的版本。按 [Support 兼容参考](references/support-compatibility.md) 核对典型控件和配置，再用项目自带 Gradle Wrapper 编译目标变体。
