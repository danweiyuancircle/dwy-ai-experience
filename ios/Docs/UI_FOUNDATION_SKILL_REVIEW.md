# UI 基础库方案与 Apple 开发 Skills 对照审查

日期：2026-11-12。记录初审与第二版文档复审。初审只新增报告；后续按用户要求补齐方案并调整 dwy-shared 的两个 Skill 源模板，未修改 ADBox 安装副本。

## 初审结论（历史记录）

**方向符合，但尚未完整满足，暂不能标记规范或组件交付通过。**

平台独立、原生优先、玻璃分层、业务隔离、主题作用域与可访问性方向已经覆盖。现有文档仍是可执行的设计/交付方案，其中部分规则还需要从原则落到明确契约；当前源码也有另行记录的实施缺口。

Skills 主要约束平台适配、架构及开发质量，不能单独证明蓝色体系、组件几何、交互手感或实际对比度已完成设计验收。

## 审查范围与证据

基础库文档：

- `ios/Docs/UI_FOUNDATION_PLAN.md`
- `ios/Docs/DESIGN_TOKENS.md`
- `ios/Docs/DESIGN_CONFIGURATION.md`
- `ios/Docs/IOS_DESIGN_SYSTEM.md`
- `ios/Docs/MACOS_DESIGN_SYSTEM.md`
- `ios/Docs/DESIGN_SYSTEMS.md`

对照 Skills：ADBox 仓库下 `.agents/skills/dwy-ios-development/`、`.agents/skills/dwy-macos-development/`、`.agents/skills/dwy-swift-development/`、`.agents/skills/dwy-apple-architecture/` 的 SKILL.md 与相关参考；已安装 `swiftui-specialist` 的 Environment 与本地化参考。下文 ADBox 路径均相对 ADBox 仓库根，全局 Skill 参考路径相对该 Skill 根。

本轮为文档及边界审查；只对基础库 `Package.swift` 的平台声明做当前源码回读，不把历史测试或图形界面证据作为本轮验收。

## 已覆盖的要求

| 要求 | 现有方案 | 结论 |
|---|---|---|
| iOS 18+、Mac 26+ 独立平台组件 | 平台规范及 DesignKitIOS / DesignKitMac 分层 | 设计方向满足，源码完成情况另列 |
| Mac 不套手机固定尺寸/布局 | Mac 规范区分 controlSize、窗口、键鼠、工具栏与多列 | 满足方向 |
| 原生组件与交互优先 | Button/Menu/Picker/Binding 原生语义，避免 Gesture 替代 Button | 满足方向 |
| 玻璃分层与版本判断 | 内容层清晰，导航/必要操作层用玻璃；iOS 18 与 26 分开 | 满足方向 |
| 系统辅助功能 | 明暗、字号、VoiceOver、减少透明度/动态效果、增加对比度 | 已有明确要求，未完成执行 |
| 主题与业务隔离 | Environment 值配置，独立 window/scene 装配；业务不进主题 | 满足方向，另有工程约束建议 |
| 跨项目抽取边界 | 独立示例、真实复用理由、业务模块可选，不复制 ADBox 单例 | 满足方向 |
| 不混淆验证层次 | 方案区分源码、测试、运行与目标系统交互/视觉 | 满足要求，实际验收未完成 |

## 需要补充的规范

### D1 — 必须补充：iOS 原型与宽度矩阵

- 依据：ADBox `.agents/skills/dwy-ios-development/references/layout.md` 第 9–17、39 行。
- 当前：`ios/Docs/IOS_DESIGN_SYSTEM.md` 第 67 行只写小屏、长文案、旋转等；未写明确的宽度档位，亦未明确 pt、容器相对布局及不使用 UIScreen.main.bounds 换算页面。
- 影响：设计者与实现者可能各取一种小屏，或把原型宽高作为代码尺寸，无法形成一致验收。
- 补充：原型基准 393×852 pt；验收宽度 375 / 393 / 430 pt；原型不等于固定页面尺寸。前景内容遵循安全区，优先 stack/grid/Spacer/safeAreaInset/容器布局，固定比例控件由外层容器适配。
- 验证：表单、底部操作区、导航/弹层分别在三档宽度、长文案和字号放大时可操作，无关键截断或横向溢出。

### D2 — 必须补充：弹层的入口、目标与平台差异

- 依据：ADBox `.agents/skills/dwy-swift-development/references/presentations.md` 第 3–5 行；两端平台 Skill 的 `references/presentations.md`。
- 当前：方案写到“锚点、多 scene、窗口归属”，但没有规定 popover / 可能作为 popover 呈现的 confirmationDialog 应挂在实际触发按钮/行上，也没有覆盖 iOS 18.0/18.1 指定 arrowEdge 的差异。
- 影响：同一公共组件在列表、滚动页、toolbar 或不同窗口内可能指错入口或业务对象；API 可能向 iOS 18.0 使用者承诺系统不保证的箭头方向。
- 补充：明确实际触发源、当前对象、来源坐标/窗口与呈现所有权；iPhone 紧凑环境允许系统适配 sheet/全屏，iPad 按尺寸类别验证。按 Skill 要求核对指定 arrowEdge 的 SDK/运行时差异，允许系统选方向时使用不指定边的重载。Mac 不套用 iPhone 紧凑适配。
- 验证：触发、滚动、列表复用、移窗/缩窗、屏幕边缘、取消后重开；确认最终动作仍对应原目标。18.0/18.1 仅对涉及该差异的呈现增加测试，不扩大所有组件矩阵。

### D3 — 必须补充：iOS 回归不能长期固定为 18 和 26

- 依据：ADBox `.agents/skills/dwy-ios-development/SKILL.md` 要求 iOS 18 与当前最新支持的大版本；受影响差异再增加中间版本。
- 当前：`ios/Docs/IOS_DESIGN_SYSTEM.md` 第 9、67 行与 `ios/Docs/UI_FOUNDATION_PLAN.md` 的部分矩阵固定 18/26，把后续大版本主要作为差异补充。
- 影响：未来组件库仍可能只验 18/26，没有覆盖当时产品支持的最新系统。
- 补充：基线矩阵定义为“最低支持 iOS 18 + 当前最新支持大版本”；iOS 26 作为玻璃首次引入节点，在相关场景保留，若与最新相同则去重；其他具体版本按已知差异增加。
- 说明：不为未公开发布的 iOS 19–25 创建测试矩阵。Skill 中 18–25 的措辞只可理解为旧样式分支范围，不能据此推断存在对应正式系统。

### D4 — 必须补充：Mac 产物级基线和架构验证

- 依据：ADBox `.agents/skills/dwy-macos-development/SKILL.md` 第 12–14 行。
- 当前：文档已约定 26/arm64、源码/模板一致与真机验收，但发布门槛没有明确写出产物回读字段。
- 补充：App、扩展、自有 helper、测试目标与本地 Swift 包的部署与架构保持一致；构建后回读 App/扩展的 LSMinimumSystemVersion、Mach-O minos，并核对发布包内实际架构。Mac 26 可用 API 可直接使用，更高系统 API 仍需可用性判断。
- 影响：仅看 deploymentTarget 或在 27 上构建，不足以证明交付产物符合 26/arm64；库的声明也不能代替消费 App 与扩展的检查。
- 验证：产物信息与包内二进制架构检查、26 系统运行、真实窗口交互/视觉分别记录。

### D5 — 必须补充：公共本地化文本契约

- 依据：已安装 `swiftui-specialist/references/localization.md` 第 31、51、68 行及 package bundle 指导。
- 当前：`ios/Docs/DESIGN_CONFIGURATION.md` 第 19 行及 iOS 组件接口主要要求“调用方传已本地化内容”；没有明确区分用户原文、已解析 String、LocalizedStringKey / LocalizedStringResource 与库资源所属 bundle。
- 影响：如果便利初始化器把标题统一收为 String，字符串字面量会在进入 Text 前失去原生可提取的本地化语义；跨包资源、占位参数与切换语言也缺少契约。显式传入已本地化 String 本身并非错误。
- 补充：可本地化 UI 文案支持原生可本地化类型或 Text/Label builder，真正的用户原文保留 String / verbatim；库自有文案从对应 target bundle 解析，支持受维护工具链上的正确 bundle 机制。动态数量、日期和列表沿用格式化资源，不拼接句子。不机械采用最低工具链不支持的宏。
- 验证：独立消费项目中 App 文案与库文案来自正确资源，含插值、长文案、语言切换及可访问名称；不能仅验证传入一段现成中文显示正常。

### D6 — 建议补充：Environment / 数据流与性能约束

- 依据：已安装 `swiftui-specialist/references/environment.md`；ADBox Swift / 架构 Skills。
- 当前：`ios/Docs/DESIGN_TOKENS.md` 第 64 行已规定类型化 Environment，但未写自定义环境键的稳定性与更新边界。
- 建议：主题使用稳定的值配置，自定义 Environment/FocusedValue 键不直接存闭包，也不靠“包进 struct”掩盖闭包的不可比较性；回调优先走组件参数，系统 openURL/dismiss 等沿用系统 Action 类型。高频进度/日志更新不放进全局设计主题。UIKit/AppKit 边界注明主线程/生命周期。
- 精确性：不能把“不 conform Equatable”单独认定为 bug；Apple 指导明确 Equatable 是比较优化路径，不是所有值类型 Environment 的必要条件。
- 验证：主题未变时不因新建闭包/对象默认值无意义刷新整个子树；高频业务更新不使所有控件重算，具体性能结论须实测。

### D7 — 交付完整性缺口：还需要真实组件规格与默认 token 定义

- 当前：现有文件给出 token 分类、组件目录和必须编写的契约，大量名称仍明确标为拟定；未形成每个组件的完整默认值/映射及状态展示。
- 判断：这不是违反某一条平台 Skill，而是尚未达到用户要求的“新项目可直接采用的专业设计规范”。平台 Skills 也不会替本库确定品牌色、间距和按钮几何。
- 补充：先为按钮、选择、输入、表单和反馈形成逐组件规格：结构、默认/可选变体、状态共存、token 引用、键盘/辅助功能、长内容布局与平台版本行为。原生系统拥有的几何记录为系统策略，不能为了表格完整填虚假的固定数字。
- 验证：默认主题能直接运行代表性页面；同一 token 修改反映到相关展示/已迁移入口；自定义色及几何通过实际场景验证后再固定。

## 当前实施层的独立缺口

这些是已知未完成项，不应混成“设计方向错误”：

1. 基础库 `Package.swift` 第 16 行仍声明 iOS 17，方案目标是 18；根清单、相关模板、支持文档与产物须在实施时统一。Mac 声明为 26 不代表所有消费方已经验证。
2. ADBox 本地 DesignKit 无条件导出 DesignKitIOS，Mac 目标也引用它；双端平台依赖分离尚未实施。
3. Mac 建议下拉原型已有明确的滚动裁剪/窗口边缘/完整辅助功能发布门槛，尚未解决；iOS 控件抽取和双端 ADBox 迁移尚未完成。
4. 本轮没有运行 iOS 18、macOS 26 或独立新项目验收；不能用之前 Mac 原型的定向测试证明全套设计交付。

## 建议处理顺序

1. 先将 D1–D5 补入对应平台规范、配置规则与验收表，统一交叉引用，避免多份矩阵互相冲突。
2. 把 D6 纳入公共组件工程规则；完成 D7 的首批组件规格和默认 token 定义。
3. 再按已有实施阶段同步源码、模板与依赖，解决原型阻断，执行目标系统与新项目接入验收。

本次审查结论为“需补充规范，交付未完成”。没有修改 Skills；未执行构建、自动测试或设备交互，也未作新的视觉/性能通过声明。

## 第二版复审与源模板调整

本节是补齐后的当前结论，以上保留初审证据。**D1–D7 的文档细则已补齐，可作为下一阶段实施基线；组件实现与目标系统验收仍未完成。** 不把“已写入要求”标记成“已测试通过”。

| 初审项 | 第二版落点 | 当前判断 |
|---|---|---|
| D1 iOS 布局矩阵 | `ios/Docs/IOS_DESIGN_SYSTEM.md` 的布局与明确验收矩阵 | 已明确 393×852 pt 原型、375/393/430 pt、相对布局与安全区 |
| D2 弹层与入口 | 两端平台规范的弹层/窗口归属章节；`ios/Docs/COMPONENT_SPECIFICATIONS.md` 的呈现承载 | 已明确触发源、对象、尺寸类别和 18.0/18.1 相关差异 |
| D3 iOS 版本矩阵 | 平台规范、总方案、配置和索引统一 | 最低 18 + 当前最新支持版，26 引入节点按相关场景保留并去重 |
| D4 Mac 产物验真 | Mac 规范及总方案的产物检查 | 已明确部署/架构一致性、LSMinimumSystemVersion、Mach-O minos 与 arm64 回读 |
| D5 本地化接口 | `ios/Docs/DESIGN_CONFIGURATION.md` 的本地化契约与组件共通契约 | 区分原生本地化文本、原文、已解析 String 和资源所属 bundle |
| D6 Environment | 配置与 token 文档的稳定值/数据流规则 | 已明确闭包、默认模型、高频更新与 MainActor 边界，不误判 Equatable |
| D7 具体组件规格 | token 第 4 节默认值/系统映射 + `ios/Docs/COMPONENT_SPECIFICATIONS.md` | 首批控件的默认、状态、事件、键盘与验收已明确；实际视觉仍待验证 |

### 两个 Skills 是否需要修改

需要小幅增强“涉及设计规范、全局 token、主题或组件抽取”时的阅读路由和通用要求，已有平台基线/布局/锚点/验收条款继续保留。具体品牌色、尺寸、状态表和 ADBox 业务只放基础库文档，不写进所有项目的通用 Skill。

本轮源模板修改：

- `dwy-cli/templates/ai-tools/skills/Apple/dwy-ios-development/SKILL.md`
- `dwy-cli/templates/ai-tools/skills/Apple/dwy-ios-development/references/design-system.md`
- `dwy-cli/templates/ai-tools/skills/Apple/dwy-ios-development/references/appearance.md`
- `dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/SKILL.md`
- `dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/references/design-system.md`

维护自审核对了四种场景：仅改文案不强制开展完整设计系统工程；已有基础库时核对实际版本并优先复用；没有该库时不强制安装；默认平台下限、arm64 和真实系统验收要求不被新路由弱化。该检查是自审，不是独立代理或真实模型触发测试。

验证记录：既有 Apple/stack Skills 发现与临时目录同步测试共 8 项通过；使用仓库已安装 YAML 解析器完成两个入口的 frontmatter、名称、描述和本地引用等价结构校验。官方 Python quick_validate 因环境缺少 PyYAML 未运行成功，未安装新依赖。文档引用、格式和原有强制条款另行回读检查；这些不能替代组件编译、设备或视觉验收。

当前仍需实施：基础库 iOS 17→18、ADBox 平台依赖分离、原型与新 token/API（包括原生本地化入口）的对齐、建议下拉阻断、完整双端组件、新项目消费及真实系统验证。本轮没有进一步改动这些产品代码。
