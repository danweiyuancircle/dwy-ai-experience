# 全局设计 Tokens 规范

日期：2026-11-12。状态：第二版默认设计基线，已明确首批值与系统策略；token 语义路径尚非全部已实现 API，当前 EControlTheme 原型仍待对齐。

## 1. 基本原则

全局表示“同一平台内有唯一、完整的默认设计来源”，不表示 iOS 与 Mac 使用相同数字。两端独立维护默认值与实现，共用可理解的语义名称和既有 DesignCore 能力。

采用三层：原始值 → 语义角色 → 组件规则。页面和业务组件使用语义/组件层；原始值集中在定义处，不能散落各页。

首版使用原生 Swift 类型、平台语义颜色与必要的资源目录。没有多工具同步需求时不另建 JSON/CSS token 引擎、代码生成器或远端热配置；未来需要设计工具同步时再扩展唯一来源，避免两份并列真相。

## 2. 默认设计

- 两端默认风格均为中性底色、清晰文字、蓝强调、克制分隔和原生材质。平台控件密度、触点、导航和呈现分别遵循各端规范。
- 默认强调蓝沿用 ADBox 当前色系，具体值见下表；静态不透明色对已计算对比，明暗、玻璃与增加对比度的真实界面仍须验证，不能把“已过 AA”注释当作当前组件组合的验收结果。
- 系统背景、正文和分隔色优先用平台语义 API，不抄系统当前 RGB。危险、错误和焦点不被品牌覆盖。
- 默认配置开箱可用；业务无需逐个配置颜色、圆角或字号。

## 3. 三层模型

| 层 | 内容 | 变更影响 |
|---|---|---|
| 原始值 Primitive | 自有品牌色、必要的间距/曲线基础值、图标比例；系统颜色直接引用系统 API | 由设计维护，不直接暴露给所有页面随意覆盖 |
| 语义 Semantic | background、surface、text.primary、accent、danger、spacing.section 等用途 | 同平台整体主题与明暗/辅助功能解析 |
| 组件 Component | button.primary、field.error、toolbar.action、notice 等已成立的规则 | 特定组件族；原生控件能管理的值不重新手算 |

这些是规范中的语义路径，不是已经存在的 Swift API。发布前在各平台以类型化结构表达，禁止 String 字典查 token 或 Any 类型擦除。

## 4. 全局 token 目录

| 类别 | 必须定义的语义 | 平台边界与规则 |
|---|---|---|
| 颜色 | background、surface、elevatedSurface、text.primary/secondary、separator、accent/onAccent、success、warning、danger、selection | UIKit / AppKit 动态语义色各自映射；不能把 separator 当正文色 |
| 排版 | title、sectionTitle、body、secondary、caption、monospaced、数字/状态所需角色 | iOS 语义字体/Dynamic Type；Mac 系统字体及产品字号；禁止统一固定成一套 13/14pt |
| 间距 | inline、controlGroup、fieldLabel、formRow、group、section、pageInset | 内部使用离散尺度；首批从 ADBox 实际间距归并，明确使用场景后固定，不追求所有现有数字原样保留 |
| 尺寸 | iconGlyph、iconHit、control、field、search、row、toolbarAction、contentWidth | 字形与触点分开；iOS 通用舒适触点以 44pt 级为基准，Mac 使用本端规范/原生 controlSize；都允许内容撑高 |
| 圆角 | field、card、group、浮动控件/容器适配 | 系统负责的按钮/窗口圆角交系统；自绘字段/卡片才引用 token，优先同心几何 |
| 边线 | separator、fieldBorder、selectionBoundary、focus 的语义 | 系统焦点优先；自绘 hairline 根据 displayScale，不能假定所有屏幕恒定 0.5pt |
| 层次 | content、navigation、floatingAction、popover、modal 的用途 | 材质与呈现分别处理；zIndex 只在局部宿主定义，不发布全局任意层级数字表 |
| 图标 | inline、control、navigation、status 的字形尺寸/weight/rendering | 优先 SF Symbols；品牌图片由应用传入，不用 emoji，不把一套图标定死给所有产品 |
| 动效 | feedback、selection、expand、presentation 的角色 | iOS/Mac 曲线与幅度分别决定；原生反馈优先，减少动态效果时提供对应策略 |
| 材质 | contentSurface、navigation、floatingAction、modalSurface | iOS 18 采用标准样式；iOS 26 与 Mac 26 按场景用玻璃；不提供“所有控件统一透明度”开关 |

### 4.1 第一版默认色与系统映射

这些是供实施使用的默认定义，不表示主题资源或全部 API 已落地。除自有品牌色外，系统语义色不抄 RGB。

| token | 默认值 / 策略 | 覆盖规则 |
|---|---|---|
| accent，普通浅色 | sRGB #2563EB | 品牌可统一覆盖，须同时定义合适的 onAccent 并验证对比 |
| onAccent，普通浅色 | #FFFFFF | 用于不透明强调底的内容，不强制覆盖系统玻璃自适应前景 |
| accent，普通深色 | #3B82F6 | 品牌覆盖须保留明暗语义 |
| onAccent，普通深色 | #0A1A33 | 深色强调底上的对比前景 |
| accent / onAccent，增加对比度浅色 | #1E40AF / #FFFFFF | 自有品牌色的高对比映射，不能关闭系统增加对比度效果 |
| accent / onAccent，增加对比度深色 | #93C5FD / #0A1A33 | 同上；静态色对目标至少 7:1，实际材质仍单独验收 |
| text.primary / secondary | SwiftUI .primary / .secondary，对应平台动态文本色 | 不允许产品为了品牌整体覆盖正文或降低对比 |
| background / surface | iOS 的 systemGroupedBackground / secondarySystemGroupedBackground；Mac 的 windowBackgroundColor / controlBackgroundColor | 封装在本端资源/映射中，随外观及系统设置变化 |
| elevatedSurface | 原生 popover/sheet/面板背景；自绘卡只用本端 surface 与明确分隔 | 不默认给内容卡套玻璃 |
| separator | 平台 separator 动态色 | 自绘 hairline 为 1/displayScale pt，系统边线不额外叠画 |
| danger / warning / success | 系统动态 red / orange / green 及原生 role | 危险色不能被 accent 覆盖，状态仍包含文字或必要图标 |
| selection / focus | 优先原生选择与焦点机制 | 自绘选中条只有在原生机制无法覆盖时引用本端语义，不用颜色单独表达 |

强调色对的静态 sRGB 对比计算：普通浅色 5.17:1、普通深色 4.72:1、增加对比度浅色 8.72:1、增加对比度深色 9.64:1。此计算只覆盖表中不透明色对；不是整套 UI、材质、disabled 或高对比模式的视觉通过证明。品牌替换也要重新验证，不能只改 accent 留下不匹配的前景。

### 4.2 排版与几何默认表

| 语义 | iOS 默认 | Mac 默认 |
|---|---|---|
| typography.title | 系统 .title2 | 系统 .title3 |
| typography.sectionTitle | 系统 .headline | 系统 .headline |
| typography.body | 系统 .body | 系统 .body |
| typography.secondary / caption | 系统 .subheadline / .caption | 系统 .callout / .caption |
| typography.monospaced | .body.monospaced()，用于原文/数字等合适内容 | 同语义，本端系统字体及产品字号 |
| spacing.inline / controlGroup | 4 / 8 pt | 4 / 8 pt |
| spacing.fieldLabel | 6 pt | 6 pt |
| spacing.formRow / group | 12 / 16 pt | 8 / 12 pt |
| spacing.section | 24 pt | 20 pt |
| spacing.pageInset | iPhone 16 pt；iPad 常规内容区 24 pt | 主内容 20 pt |
| spacing.cardInset | 16 pt | 12 pt |
| size.iconGlyph | 普通操作 20 pt；特殊导航优先系统决定 | 普通内容操作 13 pt；toolbar 16 pt，原生控件内字形按系统策略 |
| size.iconHit | 最小 44×44 pt | 普通图标操作最小 28×28 pt；toolbar/floating 最小 34×34 pt |
| size.action / field / search | 外部命中/单行外壳最小 44 pt 高，允许内容撑高 | 原生按钮由 .regular 决定；自绘单行字段最小 28 pt，搜索/过滤最小 36 pt |
| radius.field / card | 12 / 16 pt | 8 / 8 pt |
| radius.button / window / native presentation | 原生样式/容器几何 | 原生样式/容器几何 |

排版角色使用系统可缩放字体，不把默认系统字号展开为另一份静态数字表。尺寸单位是 pt，44/28/34 是实际外部命中或外壳下限，不是要求在 label 内加同等 padding。原生控件的 insets、圆角和高度可由系统确定，不能为了凑表格强行重画。

默认仅提供标准密度；Mac 的 native controlSize 可在明确工具区域使用小号，须满足该场景的命中、可读性与键盘要求。没有真实第二种布局时不另设任意密度倍率。iOS 不通过“紧凑模式”缩小触点或关闭字号放大。

新组件已实现上述标准值，Mac iconSide 已统一为 28，并由定向测试检查。ADBox 旧 token 尚未迁移；数值对齐不等于目标系统视觉与交互验收通过。

### 4.3 反馈与动态策略

- button/menu/picker/toggle 的普通反馈优先系统实现；不重复叠加自绘按压 spring。
- 自绘区域的选择/布局变化只在对应平台规范允许时动画，尊重减少动态效果；后台保活页命中、tab 切换等已有稳定性约束优先于装饰动画。
- 简短非关键成功 toast 默认显示 2 秒，消息替换取消旧计时；读屏开启时提供合适公告，焦点/交互落在提示内容时不强行计时移除。重要错误和需要用户选择的状态不走该计时策略。
- 需要长时间阅读或用户操作的 notice 使用可关闭持久呈现。禁止把全局 toast 时间当作业务请求超时。
- 动画曲线优先复用 DesignCore 已有角色；新参数只有在真实动态验收后加入，系统拥有的过渡不在 token 中仿制一遍。

## 5. 组件级规则示例

| 组件族 | 规则 |
|---|---|
| primary button | 强调色/对比前景、原生主操作语义；busy 仍保留标签 |
| secondary button | 清晰次级层次；不能因全局 tint 与主按钮失去区分 |
| destructive action | 原生 role 与危险色语义独立于品牌，确认策略由业务决定 |
| icon action | 图标与命中边界独立；accessibilityLabel 必填，不能只靠 tooltip |
| input | 正常/聚焦/禁用/校验组合；错误含文字，保留原生编辑器与输入法 |
| selection | selected 与 focus 可共存，禁用项不可选；当前值必须可识别 |
| card / row | 内容层底色、分隔和选择边界；普通内容卡不自动加玻璃 |
| feedback | success/warning/error 状态含文字和必要图标；重要错误可被持续读取 |

不要给每个属性都生成 public token。原生控件已保证的 hover/focus/disabled 效果通过原生样式保留；只有真实定制需求才增加可维护的组件规则。

## 6. 环境与覆盖解析

解析顺序：平台默认主题 → 产品品牌/允许的偏好 → 明确作用域的局部变体 → 系统外观与辅助功能适配。最后一层是必须满足的显示约束，不是可被产品覆盖关闭的选项。

- theme / placement / size 等通过 SwiftUI Environment 向子树传播；按职责分型，不构造一个含所有业务状态的大配置对象。
- 自定义 Environment/FocusedValue 不存闭包，包装进 struct 也不能修复比较问题；回调走组件参数，系统 Action 沿用系统类型。默认值不反复分配服务/模型，高频业务数据不进入主题。
- Equatable 可作为优化路径，不是所有值类型 Environment 的必要条件；按实际读取与更新行为验证，不凭缺少协议判断性能失败。
- 独立 scene/window/NSHostingView 由产品显式装配环境，不从另一个窗口的全局单例猜测。
- 配置是值与策略，不持有服务、账号、路由、任务或文件授权。
- iOS 和 Mac 组件内部各自映射 tokens；页面不写平台判断去选择材质。
- 用户系统的减少透明度、增加对比度、字号和减少动态效果不能被“保持品牌”覆盖掉。

## 7. 对 ADBox 的迁移

- `ios/Sources/Foundation/DesignKit/Palette.swift`：品牌色与通用语义分离；旧 gold 等名称先在 ADBox 薄适配中映射，避免一次性修改所有页面。
- `ios/Sources/Foundation/DesignKit/ControlTokens.swift`：冻结表混有桌面规格，按平台用途重新归类。既有产品行为需验证后再调整，不能整体搬入公共层。
- `ios/Sources/Foundation/DesignKit/ButtonStyles.swift` 与 MacPressStyle：按使用场景归并反馈策略，已有 DesignCore Motion/ScalePressButtonStyle 先核对，避免重复样式。
- 旧页面只允许通过临时桥接访问新主题，不长期保留第二套颜色/材质/尺寸来源。迁移完成后删除被替代的定义并更新测试。

## 8. 维护与校验

- 每个 token 记录用途、平台、默认来源、允许的覆盖、辅助功能和受影响组件；数字表与代码不各维护一份。
- 新增 token 前先查原生能力及已有语义；不得为一次页面的 1pt 特例污染全局规范。
- 默认主题改动需同时更新组件展示、视觉证据和变更说明；不能把影响全部产品的默认尺寸变更伪装成无影响修复。
- 检查仅针对组件管理的外观属性；图表坐标、画布、业务数据和测试常量不纳入“禁止所有数字”的粗暴扫描。
- 自动检查覆盖 API 类型、资源完整性、主题解析与有意义的状态结果；静态硬编码扫描作为辅助，不能代替视觉和行为验收。
- 自绘主题与所有关键控件组合分别验证对比、长文本、触点和系统设置。已规定的设计值仍须标记其视觉验收状态，不能把规范有默认值当作界面已经达标。

官方依据：[Color](https://developer.apple.com/design/human-interface-guidelines/color)、[Materials](https://developer.apple.com/design/human-interface-guidelines/materials)、[Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)。
