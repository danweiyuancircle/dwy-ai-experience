---
name: dwy-android-java
description: 编写、修改、排查或评审 Android 项目中的 Java 代码时使用，适用于 Android Support 与 AndroidX，包括 Java 接口、线程、回调和组件生命周期。
---

# Android Java 开发

- 先定位目标模块、构建变体与调用方，核对 `compileOptions`、Gradle 所用 JDK、`minSdk` 和 desugaring 配置。分别判断语言语法、Java 标准库及 Android API 是否可用，沿用模块的工具链和现有依赖。
- 根据模块依赖和实际 import 选择平台或兼容类。Support 项目使用已采用的 `android.support.*` 类与注解，AndroidX 项目使用已采用的 `androidx.*` 类与注解。修改 API 或引入库时核对调用方与传递依赖。技术栈迁移由明确的迁移任务处理。
- 保留 Java 与 Kotlin 调用方的类型、可空性和回调契约。使用具体的泛型类型及模块现有的空值注解，外部数据进入业务逻辑前验证。对导出的类和方法用 Javadoc 说明用途以及调用方必须遵守的线程、生命周期等约束。
- 沿用项目已有的异步机制。耗时操作在后台执行，View 更新在主线程进行。按组件生命周期解除自己注册的监听和回调。Fragment 中引用 View 的字段、监听与适配器按 View 生命周期清理，避免页面退出后迟到回调访问已销毁的界面。
- 使用项目 Gradle Wrapper 运行目标变体编译和相关测试。改动涉及回调时，验证成功、失败和界面销毁后的回调行为。

涉及较新的 Java 语法或库 API 时，对照 [Android Java API 与 desugaring](https://developer.android.com/studio/write/java8-support)。
