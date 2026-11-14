以下是迁移自原 Swift 基线的团队约定；先遵循用户要求和现有项目约定，平台专属内容仅在相应平台使用。架构和依赖方向使用 `dwy-apple-architecture`。

## 平台约束与写法

- 系统版本、支持架构和回归范围分别使用 `dwy-ios-development`、`dwy-macos-development`，此处不重复定义。具体范围按项目上下文、共享库调用方要求决定；既有项目不因启用 Skill 自动修改工程配置。
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

## 图标视觉一致性

- 适用于 SF Symbols、SVG、PNG 及其他图像素材。同组、同层级图标应保持相近的视觉大小、笔画粗细和视觉重心，不能只检查字号、素材画布或布局框相同。
- 同组按钮的点击区域和布局尺寸统一；根据图形实际可见轮廓、透明留白、内部留白和长宽比例，微调图标显示尺寸与对齐。保持原始比例，不通过非等比拉伸强行统一宽高。
- 同组优先使用同一套素材和相同字重。在实际界面、实际显示尺寸下并排验收；明显偏大、偏小、偏轻或偏移时须修正，不能只验代码参数。

## 按钮语义与样式一致性

- 相同功能、相同层级、相同状态的按钮，在不同页面保持一致的颜色、色调、强调程度、图标风格和交互反馈；例如普通工具操作的「刷新」不能在不同页面随意改成蓝色强调或灰色弱化。
- 主要、次要、普通工具和危险操作，以及正常、悬停、按下、选中、禁用、加载状态，统一映射到项目已有组件变体和语义 token；不在各页面独立指定配色和状态样式。
- 仅在操作层级、状态或背景环境确有差异时调整表现，并保留相同语义和辨识度。深浅色模式分别使用统一映射，不要求机械复用同一色值；不覆盖原生危险语义或破坏可访问性。
- 验收时跨页面对照同类操作的颜色、强调程度和状态反馈，不能只看单个页面是否协调。

## 重复能力封装与复用

- 新增入口前，先查已有公共方法、组件、服务和基础库。多个实际入口的行为与约束相同且存在重复实现时，应合并为公共入口，调用方只传必要的内容、上下文和动作；不在各页面重复系统调用、参数拼装、状态处理和反馈。
- 例如同一分享功能出现在 3 个或 10 个位置时，共用分享按钮、组件或操作实现；样式复用用组件或 ButtonStyle，行为复用用方法或服务，按现有结构选最小合适形式，不强制全局单例。
- 只抽真正相同的部分；业务内容和权限判断留在对应业务层，弹窗锚点、宿主窗口及生命周期上下文由实际入口提供，不查找全局首个窗口或视图来替代。保留原生分享、菜单、导航与平台控件契约。
- 一次性实现留在原处，不机械包装每个系统 API，不为假设复用新增协议、配置或层级；跨 Feature 与跨产品的落点按 `dwy-apple-architecture` 判断，不自动扩大为基础库迁移。
- 抽取时同步替换授权范围内所有同类调用方，并验证各入口的内容、成功、取消、错误处理和受影响平台行为；样式调整应能通过公共实现一致生效，既有校验和错误处理不得丢失。

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
