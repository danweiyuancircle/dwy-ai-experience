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

## 动效

- 默认优先 `spring`，用同一组参数避免风格撕裂。

```swift
private let motionSpring = Animation.spring(response: 0.5, dampingFraction: 0.75)
```

## 图标与文案

- 图标优先 `Image(systemName:)`，无符号则用成熟 SVG。
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
