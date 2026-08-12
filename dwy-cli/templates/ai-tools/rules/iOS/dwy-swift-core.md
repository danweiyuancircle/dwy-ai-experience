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

### 临时代码标识（强制）

产品源码中的业务待办、调试旁路、假数据**必须**用固定标签（`//`，勿写进正式 `///` 文档注释）。单元测试 / UITest 正规 mock **不强制**。

| 标签 | 用途 | 格式 |
|---|---|---|
| `TODO` | 业务/技术未完成 | `// TODO(name, YYYY-MM-DD): 说明`（推荐） |
| `TESTCODE` | 临时调试、跳过生物识别/鉴权等 | `// TESTCODE: 说明 + 移除条件` |
| `MOCK` | 假数据、stub Service | `// MOCK: 说明 + 将来替换点` |

- 写 mock/调试的**同一 diff 必须带标**；接真实现后**删标签与包夹**
- 禁止无标签假返回；禁止自造 `// 假数据` 等替代词
- 发版/提测前搜 `MOCK`、`TESTCODE`，清单确认（允许残留但须知情）

**单行**（仅一行代码）：

```swift
// MOCK: 个人资料假数据，接 ProfileService.fetch 后删除
let profile = Profile(name: "Demo", avatarURL: nil)

// TESTCODE: 跳过生物识别，提测包删除
// return true
```

**多行 / 大段（≥2 行逻辑）强制包夹**：

```text
// MOCK BEGIN: <说明 + 将来替换点>
...
// MOCK END

// TESTCODE BEGIN: <说明 + 移除条件>
...
// TESTCODE END
```

```swift
// MOCK BEGIN: 个人资料假数据，接 ProfileService.fetch 后删除
let profile = Profile(
    name: "Demo",
    avatarURL: nil,
    roles: ["user"]
)
// MOCK END
```

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

## 打包与版本号

- **build 号用时间戳**：`CFBundleVersion` 每次打包设为 `date +%Y%m%d%H%M`（如 `202606231415`）。时间戳天然唯一递增，满足 TestFlight / App Store「build 号唯一递增」要求，免去人工记号撞号。
- marketing version `CFBundleShortVersionString`（如 `1.0`）按发布节奏手动改，不随每次打包变。
- 用 XcodeGen 的工程，`xcodegen generate` 会按 `project.yml` 重写 `Info.plist` 把 build 号覆盖回默认值。顺序必须 **先 `xcodegen generate`、再 `PlistBuddy -c "Set CFBundleVersion <时间戳>"` 设号、最后 archive**，别反。
- 归档产物放工程内固定目录（如 `build/`）并加 gitignore，不用 `$TMPDIR` 临时目录。
- changelog 维护在 iOS 端目录下（如 `ios/CHANGELOG.md`），发版前按「新增 / 变更 / 修复」记本次相对上版的用户可感变化。
