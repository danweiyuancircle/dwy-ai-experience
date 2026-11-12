# macOS 设计规范与组件抽取方案

日期：2026-11-12。状态：第二版设计基线，已补齐 Skill 对照细则；已存在部分 Mac 原型，不等于稳定组件已交付。

完整组件目录与交付标准见 `ios/Docs/UI_FOUNDATION_PLAN.md`；tokens 和配置遵循 `ios/Docs/DESIGN_TOKENS.md`、`ios/Docs/DESIGN_CONFIGURATION.md`。本文件负责 Mac 的平台差异，不重复维护另一份全局 token 表。

## 平台目标

- macOS 26.0+、Apple Silicon；新组件直接使用 macOS 26 的原生 API，不添加 macOS 14/15 兼容分支。
- 独立维护 `DesignKitMac` 的规范、公开接口、展示和测试，不导入 DesignKitIOS。
- 以 ADBox 的桌面表单、工具栏、按钮和菜单为抽取依据；保留原生键鼠、快捷键、窗口与辅助功能语义。
- 与 iOS 共用语义概念，不共用触点数值、布局、导航或弹层生命周期；详见 `ios/Docs/DESIGN_SYSTEMS.md`。

## 视觉与交互规范

| 维度 | Mac 约定 |
|---|---|
| 内容层 | 日志、终端、表格、文件与镜像正文清晰稳定，不整体透明化 |
| 导航/操作层 | 系统 toolbar 优先；必要浮动操作使用原生玻璃；相关形状由父操作组统一管理 |
| 字号与密度 | 优先系统正文与 controlSize；支持产品字号，不能把 iPhone 大触点直接用于桌面密集工具区 |
| 触点与形状 | 区分字形和命中尺寸；完整按钮背景可点；保留系统焦点，尺寸值应由本端主题集中控制并允许内容撑高 |
| 主次与危险 | primary、secondary、plain 分层；destructive 不能被品牌 tint 淹没；busy 仍保留可访问名称并禁止重复触发 |
| 输入 | 原生文字编辑、IME、自动填充、安全输入和标准编辑快捷键；不在组件里校验设备或命令语义 |
| 键鼠 | hover、press、focus、Tab、Enter/Esc、help、右键、键盘操作菜单；不能用单纯手势代替原生 Button |
| 窗口 | 可缩放、明暗/活动状态、全屏；独立窗首次点击/焦点/环境注入单独处理 |

内容区、浮动操作、系统工具栏是材质使用场景，不是业务路由。基础组件不能修改 NSWindow 的全局 toolbar 策略或应用快捷键登记。

## 弹层与窗口归属

- 指向入口的 popover / confirmationDialog 关联实际触发按钮或行；列表、toolbar 和自定义坐标须保留来源对象及所属窗口。普通居中 alert 不按箭头锚点处理。
- Mac 不套用 iPhone 的紧凑尺寸 sheet 适配。允许系统选方向时用不指定边的原生重载；指定边时验证窗口移动、缩放和屏幕边缘约束。
- 取消、外部点击是否关闭、Enter/Esc、焦点返回及非激活窗首次点击属于明确契约；通用组件不查找应用首个窗口代替真实来源，也不擅自注册全局快捷键。

## 产物级基线与架构验真

- App、扩展、自有 helper、测试目标、本地 Swift 包的部署下限统一 26.0；XcodeGen、构建设置与支持说明一致。高于 26 的 API 仍须可用性判断，不能以当前 SDK 版本推断目标系统可用。
- 构建后回读 App/扩展 Info.plist 的 LSMinimumSystemVersion 和每个相关 Mach-O 的 minos；检查发布包、二进制依赖与自有可执行文件的实际架构均符合 arm64 交付范围。
- SPM library 的平台声明不能代替消费 App/扩展检查。源码声明、产物检查、26 系统启动、实际交互和视觉验收分别记录；不以在 27 上构建或运行代替最低目标系统。

## 组件与实际来源

以下 ADBox 路径相对 ADBox 仓库根；公共落点为基础库 `ios/Sources/macOS/DesignKit/`。

| 组件族 | ADBox 当前来源 | 目标边界 |
|---|---|---|
| 操作/图标按钮 | `ios/Mac/Chrome/EButtons.swift`、`ios/Mac/Chrome/MacIconButton.swift`、`ios/Mac/Chrome/MacPressStyle.swift` | 主次、标签、role、busy、disabled 与材质集中；锁标和 Pro 门控留业务；不强行统一卡片按压与玻璃按钮 |
| 动作菜单 | `ios/Mac/Features/Session/MacDeviceActionBar.swift`、`ios/Mac/App/MacToolsMenu.swift` 等 | 原生 Menu 内容 builder 保留 Button/Toggle/Section/子菜单；设备动作与工具目录不进入库 |
| 单选/分段 | `ios/Mac/Features/Settings/MacSettingsPane.swift`、`ios/Mac/Features/Apps/MacAppsPane.swift`、`ios/Mac/Features/Logs/MacLogcatPane.swift` 等 | 原生 Picker 绑定与呈现独立；不能用自画菜单丢掉当前值、禁用项或键盘行为 |
| 文本/密码/搜索 | `ios/Mac/Chrome/MacFormField.swift`、`ios/Mac/Features/Tools/MacSigningPane.swift`、`ios/Mac/Features/Files/MacFilesPane.swift` 等 | 抽外壳与焦点/编辑语义；文件授权、密钥库、端口与业务校验留调用方 |
| 建议下拉 | `ios/Mac/Chrome/MacFilterComboBox.swift` | 过滤展示与提交协议可抽；Logcat 字段、历史写入、长度限制和 UserDefaults 键留业务。窗口边缘和滚动裁剪是稳定性门槛 |
| 表单行/动作组 | `ios/Mac/Chrome/MacFormField.swift`、`ios/Mac/Chrome/EButtons.swift` | 标题、说明、校验与右对齐动作；长内容可滚动、主次操作不被裁掉 |
| 轻提示/确认/进度 | `ios/Mac/Chrome/MacNoticeHost.swift`、`ios/Mac/Chrome/MacConfirmAlert.swift`、`ios/Mac/Chrome/MacBusyOverlay.swift` | 抽展示与明确的宿主协议；普通提示非模态，重要确认模态；不直接依赖 MacAppModel 或复制 ADBox 根壳状态机 |
| 页内承载/弹层 | `ios/Mac/Chrome/MacHostSheet.swift`、`ios/Mac/Chrome/MacFormSheet.swift`、`ios/Mac/Chrome/MacInCardPage.swift` | 后续单独评审呈现协议；蒙层洞、toolbar 阻断、红绿灯放行及 Escape 所有权不能随材质调整丢失 |

优先抽稳定的基础控件，再处理与宿主窗口密切相关的呈现。表格、快捷指令抽屉、设备 tab、多会话保活不直接整体搬入控件库。

## 当前原型与需要收敛之处

目前公共库已写入：

- `ios/Sources/macOS/DesignKit/EControlTheme.swift`：主题、场景、输入外壳。
- `ios/Sources/macOS/DesignKit/EButtons.swift`：EButton、EIconAction、EActionGroup。
- `ios/Sources/macOS/DesignKit/ESelectionControls.swift`：EMenu、EPicker、ESwitch。
- `ios/Sources/macOS/DesignKit/EFields.swift`：ETextField、ESecureField、ESearchField、EField。
- `ios/Sources/macOS/DesignKit/EComboBox.swift`：建议下拉与输入法键盘守卫。

这些是从 ADBox 需求提炼的原型接口，尚未发布，ADBox 仍使用旧版本依赖。后续按本规范收敛，不能为了已写入而冻结不足的接口。

发布前必须解决：

1. 建议下拉在 ScrollView、窄窗与上下边缘的呈现，不能被父层裁掉，也不能点穿下层；需比较原生控件与合适的原生弹出承载，保留禁用自动补全及中文组合输入约束。
2. 完整 VoiceOver 选择语义、展开状态、键盘关闭、失焦提交契约及动态候选更新；不把业务历史持久化悄悄移入组件。
3. 主次按钮在品牌强调色下仍可区分；危险角色保持明确，busy 标签可被辅助功能读取。
4. 所有支持尺寸与系统辅助功能配置，特别是大字号、增加对比度、减少透明度和减少动态效果。
5. macOS 26 实机与真实应用宿主验收；当前 27 上的展示与测试不能代替。

## 主题与接口

- 主题提供 Mac 语义颜色、控件/表单/搜索尺寸和必要圆角；ADBox 冻结 token 仅作来源，不把其所有固定值变成公共规范。
- 原生控件支持的 ButtonRole、controlSize、keyboardShortcut、Binding、Label 沿用；API 不重复包装原生状态。
- 材质与基本状态集中在少量内部样式处；页面不再自行添加玻璃、圆角、描边、按压和禁用颜色。
- 同一业务动作可以在各场景复用组件，但 toolbar 与独立浮动区域不能都强制画一层相同背景。
- `EField` 不决定业务校验；`EMenu` 不持有应用路由；`EActionGroup` 不向全局注册快捷键；组件库不记录用户密码、设备或账号票据。
- 文案从调用方传入或使用库自身完整本地化资源，不读 ADBox loc 单例或要求应用必须存在某些 key。

## 验收与迁移

1. 公开接口独立展示：`ios/Examples/MacControls/Sources/MacControlsGallery/MacControlsGallery.swift`，只 import DesignKitMac，不引用 ADBox。
2. 组件测试：`ios/Tests/DesignKitMacTests/`，覆盖下拉候选/导航/输入法、长文本布局、主题尺寸及原生选择/菜单组合。
3. 真实窗口：明暗、活动/非活动、各种控件状态、窄窗、大字号、多窗口、键盘、VoiceOver 和辅助功能；动态布局保留中间帧证据。
4. 基础库版本发布后，ADBox 的 Mac wrapper 接入已发布固定版本；保留锁标、快捷键作用域、数据备份与任务生命周期。Mac 不导出 iOS ThemeManager。
5. 逐页替换分散实现，再删除被替代的自绘外观；必要业务组合继续留在 ADBox。完成后统计剩余手写外观及其保留理由，而不是追求把所有 Button 语句归零。

官方依据：

- [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Build an AppKit app with the new design](https://developer.apple.com/videos/play/wwdc2025/310/)
- [Native controls](https://developer.apple.com/documentation/swiftui/controls-and-indicators)
