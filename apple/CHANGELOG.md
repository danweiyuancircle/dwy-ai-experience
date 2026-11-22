# Changelog

Apple App Kit（统一公开仓库中的 Apple 产品）版本记录。
**已上线的 App 默认不升级。** 要不要 bump，只看本节：兼容性、破坏面、不升会少什么。不要靠读 diff。

当前远程：https://github.com/danweiyuancircle/dwy-ai-experience.git
发版 = 改本文件 + 打 **同号 git tag**（首个完整私有发布版本 `0.4.1`）。

## 版本规则（0.x）

| 升 | 含义 | 已上线 App |
|----|------|------------|
| **patch**（0.2.0 → 0.2.1） | 只修 bug / 加文档，旧调用必须还能编、行为兼容 | 可不升 |
| **minor**（0.2.0 → 0.3.0） | 允许破坏 API 或持久化键 | **不要跟**，除非你主动要新能力并改完 App |
| **major**（1.0.0） | 公开稳定面；之后才按 SemVer 1.x 的 major=破坏 | — |

`Package.swift` 写 `from: "0.2.0"` 在 0.x 里等于 `>=0.2.0 <0.3.0`。`Package.resolved` 钉死具体 revision。
禁止 `path:` 本地源码，禁止 `branch: main`。

每一节必须有 **兼容性** 四行，缺一行不准打 tag。

每次更新版本、Changelog 或创建/发布语义化 tag 前，必须对照上一发布 tag 检查 `dwy-cli/templates/ai-tools/skills/Apple/dwy-apple-appkit/SKILL.md` 与受影响的平台引用资料。版本条目记录“Skill 同步检查”及更新路径；无需更新时写明具体依据。需要同步的内容必须进入同一个新 tag，不能把源码变更视为 Skill 已同步。详细要求见根 `AGENTS.md`。

当前工作区目录为 `apple/`；下面历史版本中的旧目录与迁移事件保留发布时原文，不将历史 `ios/` 目标改写为新目录。

---

## 0.12.0 - 2026-11-22

- `DesignKitMac` 默认采用 ADBox macOS 的冷静蓝、分层灰阶与语义状态色。系统明暗和增加对比度外观使用同一套主题角色。标准正文为 13 pt，次要文字为 11 pt。
- 新增 `ETypography(bodySize:)`，统一应用自定义字体和 AppKit 编辑器字号。设置页、Toast 和新建 macOS 工程首页读取共享主题，应用可按窗口或子树覆盖。这次变更仅涉及 macOS 主题与共享版本锁定。
- Skill 同步检查已更新 `dwy-cli/templates/ai-tools/skills/Apple/dwy-apple-appkit/SKILL.md` 和 `dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/references/design-system.md`，记录默认主题、字号入口和应用覆盖方式。iOS 与 Swift 通用开发规则无需更新，iOS UI、依赖初始化和工具链要求未变。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.11.0 能否不改 App 继续编 | 可以。公开 API 保留，使用标准主题的 macOS 页面会采用新的默认配色和字号。 |
| 不升会怎样 | 继续使用原主题与字号，无法通过 `ETypography(bodySize:)` 派生应用的字号档。 |
| 升上来可选/必改项 | 无必改调用。重新验收浅色、深色和增加对比度外观。自设品牌可继续使用现有主题环境覆盖。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0，均未提高。 |

## 0.11.0 - 2026-11-19

- 移除 DesignKitMac `eWindowOverlay`。页内叠加弹框需要自行拦截鼠标、键盘、快捷键、菜单与焦点，范围难以完整覆盖；模态弹框统一改用 SwiftUI `.sheet` / `.alert` / `.confirmationDialog` 或 AppKit sheet。
- Playground 平台对话框演示改为原生 `.sheet`，示例启动参数改为 `--platform-host-preview`；删除对应 9 项页内弹框测试。`ePreventsSidebarCollapse` 保留。
- Skill 同步检查：已更新 `dwy-cli/templates/ai-tools/skills/Apple/dwy-apple-appkit/SKILL.md`、`dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/SKILL.md`、`dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/references/presentations.md` 和 `dwy-cli/templates/ai-tools/skills/Apple/dwy-swift-development/references/presentations.md`，要求模态弹框使用系统模态并禁止页内叠加模拟模态，记录迁移方式。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.10.1 能否不改 App 继续编 | 不能。调用 `eWindowOverlay` 的 App 编译失败，其余公开 API 不变。 |
| 不升会怎样 | 0.10.x 继续可用，但页内弹框的输入隔离边界仍需宿主自行补齐。 |
| 升上来可选/必改项 | 必改：把 `eWindowOverlay` 面板内容迁入 `.sheet`，删除为其补的菜单阻断和事件监听，重新验收键盘与焦点。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0，均未提高。 |

## 0.10.1 - 2026-11-18

- 修复 DesignKitMac `eWindowOverlay` 的模态输入隔离：禁用底页 SwiftUI 控件及快捷键，拦截所属窗口内面板之外的鼠标和手势输入，保留透明背景，不绘制灰色蒙层。
- 弹框自动获得焦点，Tab / Shift-Tab 不进入底页；关闭后恢复焦点，多层弹框仅最上层响应，窗口关闭时清理监听。面板快捷键和文本编辑保留 AppKit 原生分发。
- 补充 SwiftUI 挂载、透明像素、焦点、普通输入、多行 Return、快捷键、层级与监听清理测试；新增透明模态演示入口，同步生成器与 Playground 版本。
- 明确宿主须使用同一呈现状态禁用应用级业务菜单及自行安装的事件监听，不能将页内承载当作全应用模态会话。
- Skill 同步检查：已更新 `dwy-cli/templates/ai-tools/skills/Apple/dwy-apple-appkit/SKILL.md`、`dwy-cli/templates/ai-tools/skills/Apple/dwy-swift-development/SKILL.md`、`dwy-cli/templates/ai-tools/skills/Apple/dwy-swift-development/references/presentations.md` 和 `dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/references/presentations.md`，覆盖输入隔离、透明背景、焦点及宿主边界；iOS 复用共通规则，无独立 API 或最低系统变化。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.10.0 能否不改 App 继续编 | 可以。公开调用签名保持不变，修复既有模态行为；底页控件显示正常禁用样式。 |
| 不升会怎样 | 0.10.0 继续可用，但页内弹框不提供本版完整的焦点及底页快捷键隔离。 |
| 升上来可选/必改项 | 需要修复时精确锁定 0.10.1；检查宿主已有焦点拦截逻辑，避免重复处理，并按文档阻断应用级业务菜单与自定义监听。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0，均未提高。 |

## 0.10.0 - 2026-11-18

- DesignKitMac 新增 `eWindowOverlay`，在窗口内容区居中呈现无蒙层的自定义弹框，随内容区缩小并拦截底页点击。宿主提供内容、呈现状态及焦点策略。
- DesignKitMac 新增 `ePreventsSidebarCollapse`，用于 SwiftUI 原生分栏的侧栏内容。
- 同步生成器、接入示例和 DesignKitMac Playground 的版本。
- Skill 同步检查：已更新 `dwy-cli/templates/ai-tools/skills/Apple/dwy-apple-appkit/SKILL.md`、`dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/SKILL.md` 和 `dwy-cli/templates/ai-tools/skills/Apple/dwy-macos-development/references/presentations.md`，覆盖无蒙层、组件复用及宿主交互职责。iOS 和通用 Swift 的接入约束未受影响。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.9.0 能否不改 App 继续编 | 可以。新增两个 macOS 视图修饰器，现有 API 保留。 |
| 不升会怎样 | 0.9.0 继续可用，缺少页内弹框与侧栏防折叠修饰器。 |
| 升上来可选/必改项 | 需要时锁定 0.10.0 并按 macOS 文档接入新修饰器。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0。 |

## 0.9.0 - 2026-11-17

- 新增 20 个按需权限产品：共享状态与请求合并、iOS 分权限申请、macOS 系统设置引导和可选 PermissionUI；保留 limited、restricted、provisional、unknown 等真实状态，不把设置跳转成功当作授权成功。
- 纳管 PermissionsKit 12.0.0 与 PermissionFlow 2.11.4 的固定上游源码、MIT 声明与补丁记录；权限产品按需链接，不自动向宿主添加用途声明或权益。
- DesignKitIOS 新增 EAlert、EConfirm、EErrorAlert 三个公开 ViewModifier，以 .modifier(...) 使用；保留原生确认、取消与危险角色，错误消息关闭清空，不隐式重试。
- Apple 工作区从 ios/ 迁至 apple/，仓库根 Package.swift 和原有 SwiftPM 产品名保持；模板统一 App、Features/BusinessUI、BizFoundation、AppleAppKit 四层，支持 ios、macos、apple 形态和保留既有端配置的 --add-platform。
- 生成器、Playground 和当前接入示例同步精确版本 0.9.0；恢复历史 0.8.1/0.8.2 发布记录。CI 增加 macOS 26 / 27 ARM64 双环境及权限目标编译，模板回归使用真实 XcodeGen 和 SwiftPM 工具。
- Skill 同步检查：已更新 dwy-cli/templates/ai-tools/skills/Apple/dwy-apple-appkit/SKILL.md，及 dwy-apple-architecture、dwy-ios-development、dwy-macos-development、dwy-swift-development 对应规则和引用资料，覆盖目录迁移、四层模板、权限产品与新弹框的调用和生命周期约束。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.2 能否不改 App 继续编 | 原有 SwiftPM 产品及 API 保留；引用仓内旧 ios/ 路径的脚本需改为 apple/。新生成工程的目录结构改变，既有应用不自动迁移。 |
| 不升会怎样 | 0.8.2 继续可用，但缺少权限产品、iOS 三类系统弹框和新版四层脚手架。 |
| 升上来可选/必改项 | 精确锁定 0.9.0 并更新 revision；权限按需链接，宿主配置用途声明、entitlements、签名与业务恢复；导入新增弹框时使用公开大写 E 类型。已有应用不自动升级。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0；权限第三方源码随仓库纳管，既有产品不隐式依赖全部权限框架。 |

## 0.8.2 - 2026-11-17

- 包含 0.8.1 的 macOS 共享 UI 回收；修复应用图标回归中依赖 TIFF 二进制逐字一致的错误假设，改为验证真实应用图标、显式应用路径与缺失应用符号语义。
- 0.8.1 标签保留，发布 CI 因上述测试在 macOS 26 上失败，未创建正式 Release；本版使用新标签重新完整验证，不覆盖历史标签。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.0 / 0.8.1 能否不改 App 继续编 | 可以，0.8.2 仅修正测试及发布版本，运行时 API 与 0.8.1 一致。 |
| 不升会怎样 | 0.8.0 缺少新增共享 UI 入口；0.8.1 不包含本次 CI 测试修复。 |
| 升上来可选/必改项 | 消费新组件的项目精确锁定 0.8.2 并更新 revision，保留原有取消与授权流程。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0、Swift 6.0；第三方运行时依赖未变。 |

## 0.8.1 - 2026-11-17

- macOS 新增共享页头、设置页、操作行、侧栏项、管理列表、可排序列表、应用图标和进度面板组合，统一使用 DesignKitMac 的主题与语义令牌。
- 新增 EAlert、EFileDialog、EToolPanel、EToolWindow 和 ESettingsWindowChrome，集中管理平台展示与系统适配；文件授权、危险操作和任务生命周期继续由调用方负责。
- EContentState 增加可选图标，ELabelValue 支持 Text 标题；补齐八个 Playground 目录入口、中英说明、可复制示例及平台宿主演示。
- 保留旧 API；本次正式版不纳入其他工作区中的目录迁移或权限模块开发。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.0 能否不改 App 继续编 | 可以，新增 API 和可选参数保持现有构造入口兼容。 |
| 不升会怎样 | 既有功能继续可用，但无法消费新的页面组合与平台展示入口。 |
| 升上来可选/必改项 | 需要新组件的项目精确锁定 0.8.1 并更新 revision；迁移系统弹框时保留取消、错误和 security scope 的业务处理。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0、Swift 6.0；第三方运行时依赖未变。 |

## 0.8.0 - 2026-11-16

- AppleAppKit 全部 iOS / macOS 基础模块统一转为正式版 0.8.0；Playground 目录、双语说明和复制资源同步正式版本，历史 Beta 标签与验证记录保留。
- 两端新项目生成器统一精确锁定 0.8.0，替换 iOS 的 0.8.0-beta.4 与 macOS 的 0.4.1；同步模板回归和 Mac 架构文档入口。
- 纳入 beta.6 后已有的共享动效与 iOS 模板组件接入；本次转正不改变公开 API、第三方依赖或最低系统要求，不将历史测试扩大解释为全平台交互验收。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.0-beta.6 能否不改 App 继续编 | 可以，转正只统一版本及模板引用；共享动效为增量 API。 |
| 不升会怎样 | 原 Beta 版本继续可用，但不会获得正式版本标识及后续共享动效。 |
| 升上来可选/必改项 | 显式锁定 0.8.0 并核对 revision；从 0.4.1 升级的 Mac 项目须同时阅读 0.5–0.8 的历史兼容说明并验收宿主。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0；第三方运行时依赖未变。 |

## 0.8.0-beta.6 - 2026-11-14

- iOS 新增共享 EToast 紧凑轻提示：主题背景、细边框、圆角和状态图标，无可见关闭按钮。ENoticeHost 根据消息类型选择短暂或持续展示；原文短反馈支持 tone、自定义图标和重复触发计时，读屏与宿主生命周期沿用 ENoticeCenter。
- iOS EInlineNotice 与 Mac ENotice 默认将状态、操作同行排列，长文案、空间不足和 iOS 辅助字号允许增高，避免复制等轻反馈变成带操作的大卡片。Mac EToast 支持指定停留时长，默认两秒保持不变，ADBox 可沿用 1.2 秒。
- 保留 ENoticeHost 非泛型公开类型及原构造入口；示例、双语说明、Playground 版本和回归同步更新。拟发布的干净源码通过全量 228 项 SwiftPM 测试，其中 Mac 组件 20 项；本机 iOS 18.6 / 26.5 各完成 14 项单元及 1 项原生明暗 UI 回归。实际 App 接入与正式发布 CI 另行记录，不把组件测试等同于全产品验收。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.0-beta.5 能否不改 App 继续编 | 可以，保留现有构造入口和公开类型；新增短反馈与时长参数为可选能力。持续通知默认外观改为紧凑布局。 |
| 不升会怎样 | beta.5 继续可用，但 iOS 缺少独立轻提示视图，两端持续通知仍使用较大的卡片布局。 |
| 升上来可选/必改项 | 显式锁定 0.8.0-beta.6 并核对 revision；ADBox iOS 将原页内计时迁入共享中心，Mac 可显式传 1.2 秒。需阅读或处理的信息继续使用持久通知。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0；第三方运行时依赖未变。 |

## 0.8.0-beta.5 - 2026-11-12

- Mac EMenu 在原生 Menu 上默认使用 `titleAndIcon`，保留调用方 Label 图标；纯 Text 不制造图标，触发器 label 闭包内仍可用 `iconOnly` 覆盖。EPicker 只调整 menu 分支，segmented、tag、Binding、禁用与原生动作语义保留，公开构造签名不变。
- 更新菜单与选择器真实 fixture、复制源码、双语说明及目录版本；新增统一平台兼容记录，区分最低支持、SDK 编译、自动化与实际交互。
- 本机 macOS 27.2.1 arm64、Xcode 27.2（27B52）/ macOS SDK 27.2，最终 Mac 19 项与 Playground 7 项定向测试通过，Gallery 构建与签名验证通过，22 份 fixture / 44 份双语说明同源检查通过。候选实现曾核对普通 SF 图标、纯 Text 菜单 AX 与动作计数；最终 Menu 整体策略后的分组、子菜单和 Picker 完整 GUI 复核因 CUA 超时未完成。macOS 26 运行、完整 IME / VoiceOver 与本版 iOS 新增运行回归未验，不能将局部证据泛化为系统 27 全量适配。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.0-beta.4 能否不改 App 继续编 | 可以，公开签名未变；Mac 菜单中的 Label 默认保留图文，原生 Text 选项不补图标。 |
| 不升会怎样 | beta.4 继续可用，但 macOS 27 的菜单可能按系统默认隐藏调用方提供的图标。 |
| 升上来可选/必改项 | 显式锁定 0.8.0-beta.5 并核对 revision；需要图文的选项传 Label，纯文字传 Text，纯图标触发器在 label 闭包内声明 iconOnly，并验收实际菜单。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0；适配 macOS 27 不提高最低版本，第三方运行时依赖未变。 |

## 0.8.0-beta.4 - 2026-11-12

- Mac 的 EToast 改为紧凑的图标与文字提示，不再使用持久通知的宽卡片或显示关闭按钮；保留两秒自动消失、消息替换取消、悬停与焦点暂停、VoiceOver 公告和可访问关闭动作。重要通知仍使用 ENotice。
- Playground 目录、双语说明及生成 Index 同步当前版本，并检查文档 Package 字段与目录版本一致，避免展示过期包版本。
- 本机完整 SwiftPM 测试 228 项通过，其中 Mac 组件 19 项；新增短提示尺寸与长文换行覆盖。Playground 同源检查及文档版本回归通过；前台与完整读屏交互仍须目标系统验收。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.0-beta.3 能否不改 App 继续编 | 可以，公开构造入口保留；EToast 的关闭文案用于可访问关闭动作，不再生成可见按钮。 |
| 不升会怎样 | beta.3 继续可用，但轻提示仍是带关闭按钮的通知卡，Playground 的版本文案仍停留在 beta.2。 |
| 升上来可选/必改项 | 显式锁定 0.8.0-beta.4 并核对 revision；短成功提示使用 EToast，需要持续阅读或操作的信息仍使用 ENotice。 |
| 最低系统 | iOS / iPadOS 18.0、macOS 26.0 Apple Silicon arm64、Swift 6.0；第三方运行时依赖未变。 |

## 0.8.0-beta.3 - 2026-11-12

- Mac 浮动区域的非危险次要按钮取消显式品牌 tint，使用原生中性玻璃，避免帮助、关闭等自定义灰色图标落在饱和品牌色背景上。主操作与危险角色着色保留；公开 API、依赖及持久化键不变。EIconAction 复用同一规则，调用方无需逐页修改。
- 本机 macOS 27.2.1 的完整 SwiftPM 测试 227 项通过，其中 DesignKitMac 18 项、Playground 7 项。最终外观仍需在实际应用和目标系统验收，不能用宿主布局测试代替视觉结论。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.8.0-beta.2 能否不改 App 继续编 | 可以，公开接口未变；非危险浮动次要按钮的背景从品牌着色改为原生中性玻璃。 |
| 不升会怎样 | beta.2 继续可编译，但其浮动次要按钮仍会被显式品牌 tint 着色，自定义灰色图标可能对比不足。 |
| 升上来可选/必改项 | 显式锁定 0.8.0-beta.3 并核对 revision；确认自定义图标在明暗主题及实际材质下的对比度。主要操作和危险角色保留原着色。 |
... (+286 lines) [see remaining: rtk proxy git show HEAD:ios/CHANGELOG.md | tail -n +96]
