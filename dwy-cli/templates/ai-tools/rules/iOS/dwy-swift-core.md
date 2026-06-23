---
description: iOS 17+ SwiftUI 开发基线规则（全局适配、动画、国际化、注释）
paths:
  - "**/*.swift"
---

## iOS 目标与写法

- iOS 最低版本 17.0+，不为 16 及以下做兼容分支。
- 统一 Observation + `@MainActor`，状态对象默认 `final class`。

```swift
@MainActor
@Observable
final class TaskListViewModel {}
```

## 风格

- 4 空格缩进，不用 Tab。
- `UpperCamelCase` / `lowerCamelCase`。
- 参数过长换行，类型签名参数与返回值各占一行。
- 一行只做一件事，避免压缩表达式。

## 配置管理

- 可修改的运行时配置统一放在 `AppConfig`，避免业务层散落魔法值和可调参数。
- 默认实现必须只有一个 `AppConfig` 入口，所有配置项、开关、阈值和默认值从这里读取。
- 配置读取禁止越界分散；新参数先加到 `AppConfig`，再注入到业务逻辑。
- `AppConfig` 负责默认值、持久化键名、配置来源边界，业务层只读使用。

## 注释与控制流

- 关键类型、方法、属性必有中文 `///` 注释，写明意图和边界。
- 系统外边界校验，内部调用信任类型，不加冗余兜底。
- 统一 `guard` + early return，不要多层 `else`。
- 禁止 `try?` 吞异常；不写无意义 `value ?? default`。

## 全面屏与布局

- 默认尊重安全区；固定内容区用 `safeAreaInset` / `safeAreaPadding`。
- 全屏背景、遮罩、弹层可用 `ignoresSafeArea()`。
- 禁止使用固定状态栏高度常量。

## 软键盘

- 任何调起系统软键盘的输入控件，必须给用户提供主动关闭键盘的途径，禁止只能靠输入框自身失焦。
- 至少同时满足以下两种退出方式：
  - 点击键盘外空白区域收起：根容器加 `.onTapGesture` 把 `@FocusState` 置 `false`。
  - 滚动视图内滚动时收起：`ScrollView` 加 `.scrollDismissesKeyboard(.interactively)`。
- 多行输入或无明显空白可点的页面，额外在键盘上方放「完成」按钮收起。
- 焦点统一用 `@FocusState` 管理，不散落手写 UIKit `resignFirstResponder`。

```swift
@FocusState private var focused: Bool

ScrollView {
    TextField(loc("input_placeholder"), text: $text)
        .focused($focused)
}
.scrollDismissesKeyboard(.interactively)
.onTapGesture { focused = false }
.toolbar {
    ToolbarItemGroup(placement: .keyboard) {
        Spacer()
        Button(loc("done")) { focused = false }
    }
}
```

## 动效

- 默认优先 `spring`，用同一组参数避免风格撕裂。

```swift
private let motionSpring = Animation.spring(response: 0.5, dampingFraction: 0.75)
```

## 图标与文案

- 图标优先 `Image(systemName:)`，无符号则用成熟 SVG。
- iOS 应用图标设计稿只提供一张 `1024x1024` 的 PNG 源图，由系统生成各尺寸适配版本。
- App Icon 源图必须是直角完整方形，背景填满整张画布，禁止预裁圆角、圆角背景、透明圆角或模拟系统圆角遮罩。
- 图标主体必须预留至少 `10%` 安全边距，避免系统缩放、圆角遮罩或视觉放大时被切边。
- 文案禁止 emoji，禁止硬编码，统一 `loc("key")`。
- 禁止使用 emoji 作为功能说明、状态、提示。

```swift
Image(systemName: "chevron.right")
Text(loc("home_title"))
```

## 国际化

- 项目必须实现国际化。
- 默认实现必须包含中文和英文。
- 使用 `localizationBundle + loc()` + `LocalizationManager` + `AppLanguage` 组合。
- `loc` 必须走 bundle，不依赖默认 locale 自动解析 key。
- 语言变更持久化并刷新 `localizationBundle`，`system` 走系统首选。

## 资源与时序

- 颜色、字号走 token，不用裸值。
- 时间来源通过注入参数或测试可控入口，不直接散落 `Date()`。
