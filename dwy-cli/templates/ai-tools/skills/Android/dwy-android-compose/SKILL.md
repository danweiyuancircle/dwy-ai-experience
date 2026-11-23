---
name: dwy-android-compose
description: 编写、修改、排查或评审 Kotlin Jetpack Compose 界面时使用，覆盖状态、重组、副作用、主题、Compose UI 测试及与 Android Views 的互操作。
---

# Android Jetpack Compose

- 用 Kotlin 编写 `@Composable`。先检查目标模块实际 Kotlin、Compose 编译器或插件配置、Compose 依赖与主题。沿用已有 Material 体系、组件和设计约定。混合项目按目标页面的实际 UI 技术栈处理。
- 可复用组件通过参数接收状态、通过回调发送事件。状态归到需要读写它的最近共同所有者。短时 UI 状态用 `remember`，需要通过保存实例状态恢复且可保存的小型 UI 状态用 `rememberSaveable`，页面业务状态由现有状态所有者管理。列表需要跨重排保留条目状态时，使用稳定且唯一的业务 key。
- Composable 函数体负责描述 UI。需要协程或监听时按生命周期选择 `LaunchedEffect`、`DisposableEffect` 或组件已有的状态所有者。Effect 的 key 对应需要重启的输入，监听按相同生命周期解除。界面读取 Flow 时使用项目可用的生命周期感知 API。
- 按现有主题提供颜色、排版和尺寸，复用字符串资源。保留可访问语义与合理触摸或焦点行为。嵌入 Fragment 的 `ComposeView` 时将组合释放策略绑定到宿主 View 生命周期。用 `AndroidView` 包装 View 时明确创建、更新与资源释放的时机。
- 使用项目 Gradle Wrapper 编译目标变体，并按改动验证交互、状态恢复或互操作生命周期。用 Compose UI 测试断言用户可见行为与语义；预览用于检查布局。

按需查阅 [Compose 状态](https://developer.android.com/develop/ui/compose/state)、[Compose 副作用](https://developer.android.com/develop/ui/compose/side-effects)、[Views 中使用 Compose](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis/compose-in-views) 和 [Compose 测试](https://developer.android.com/develop/ui/compose/testing)。
