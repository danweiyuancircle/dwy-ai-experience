---
name: dwy-androidx-only
description: 用于启用了仅 AndroidX 约束的项目。修改源码、XML、Gradle 或第三方依赖时，保持 AndroidX 体系，禁止使用 Android Support Library。
---

# 仅使用 AndroidX

在本 Skill 启用的项目中维持 AndroidX 体系。先查看目标模块和构建变体的 Gradle 依赖、源码 import、XML 控件及主题配置。若目标仍依赖 Support Library，说明冲突及涉及的模块，先明确迁移范围，再改动冲突部分。

- 源码、XML、Manifest 和混淆配置统一引用当前项目使用的 AndroidX 对应类。禁止新增 `android.support.*` 引用和 `com.android.support:*` 直接依赖。相应控件和主题按目标模块已采用的 AndroidX 或 Material Components 版本编写。
- 确认当前工具链下 `android.useAndroidX` 实际启用。新增依赖应原生支持 AndroidX。若既有第三方二进制仍靠 Jetifier 转换，记录来源，沿用当前配置，待依赖升级并验证后再调整 Jetifier。
- 修改依赖后核对目标变体的依赖树和实际打包配置，检查是否混入未转换的 Support Library 类，并用项目自带 Gradle Wrapper 编译该变体。

类名和 Maven 坐标按官方映射核对。 [AndroidX 配置](https://developer.android.com/jetpack/androidx/) · [AndroidX 迁移](https://developer.android.com/jetpack/androidx/migrate)
