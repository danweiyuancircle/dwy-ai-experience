---
name: dwy-android-kotlin
description: 编写、修改、排查或评审 Android 项目中的 Kotlin 代码时使用，覆盖类型与空值、Java 互操作、协程和 Flow，适用于 Views、Compose 及非 UI 代码。
---

# Android Kotlin 开发

- 先确认目标模块的 Kotlin 插件版本、语言级别、JVM target 和实际依赖。沿用模块的格式化规则和现有异步方案。新增语法或 API 采用当前工具链支持的写法。
- 使用明确的可空类型表达契约，尤其要检查 Java 平台类型。对网络、文件和外部 SDK 数据在入口校验。根据字段语义处理缺失值，只有调用链能证明非空时才考虑强制断言。
- 修改 Java 仍在调用的 API 时，核对空值注解、方法签名、默认参数和异常行为。需要暴露 JVM 互操作注解时以调用方为依据。对导出的类和函数用 KDoc 记录用途及非显然的调用限制。
- 协程使用与任务生命周期一致的作用域。页面或 ViewModel 所属任务随所有者取消，确需跨页面继续的任务由明确的更长生命周期所有者负责。阻塞 I/O 调度到适合的 dispatcher，捕获异常时保留协程取消语义。
- 对 UI 收集 Flow 时，按现有依赖及宿主使用生命周期感知方式。Fragment 里跟随 View 生命周期。供 UI 读取的状态从所有者对外暴露只读接口，按项目方式验证状态变化、异常和取消。
- 使用项目 Gradle Wrapper 运行目标变体编译与相关测试。涉及 Java 互操作时把真实 Java 调用方也纳入验证。

按需查阅 [Kotlin 编码约定](https://kotlinlang.org/docs/coding-conventions.html)、[Android Kotlin 与 Java 互操作](https://developer.android.com/kotlin/interop) 和 [Android 协程实践](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)。
