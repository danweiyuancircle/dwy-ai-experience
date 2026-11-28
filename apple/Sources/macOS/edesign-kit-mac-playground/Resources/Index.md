# DesignKitMac Playground · 0.11.0

Platform: macOS 26.0+ · Module: DesignKitMac · Product: DesignKitMacPlayground

Generated from compiled fixtures and bundled Markdown. Runtime GUI, IME, VoiceOver and dynamic material acceptance are separate.

## designkit.mac.button

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ButtonExample.swift`

# EButton

ID: designkit.mac.button
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Trigger an explicit action with native primary, secondary, plain, destructive, busy and disabled semantics.

## Capabilities
- Emphasis — primary, secondary or plain; the style follows the control placement (content, toolbar, floating glass).
- Role — ButtonRole.destructive switches the tint to the danger color.
- Busy — isBusy shows a small spinner and disables only this button.
- Custom label — a ViewBuilder label accepts SF Symbols or images; icon-only labels need an accessibility name.

## Parameters, state and constraints
The caller owns execution, errors and completion. Busy blocks only this button; the fixture increments a local count.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EButton

ID: designkit.mac.button
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
触发明确操作，保留原生主次、危险、忙碌和禁用语义。

## 能力
- 强调度 — primary、secondary 或 plain，样式随控件层级（内容、工具栏、浮动玻璃）变化。
- 角色 — ButtonRole.destructive 将着色切换为危险色。
- 忙碌 — isBusy 显示小型进度并仅禁用当前按钮。
- 自定义标签 — ViewBuilder 标签可放 SF Symbol 或图片，仅图标时必须提供可访问名称。

## 参数、状态与约束
执行、错误和完成由宿主负责。忙碌仅禁用此按钮；示例只增加局部计数。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ButtonExample: View {
    private let bundle: Bundle
    private let isBusy: Bool
    @State private var count = 0

    init(bundle: Bundle = .main, isBusy: Bool = false) {
        self.bundle = bundle
        self.isBusy = isBusy
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EButton(resource("Primary action"), emphasis: .primary, isBusy: isBusy) { count += 1 }
                .accessibilityIdentifier("playground.designkit.mac.button.primary")
            EButton(resource("Secondary action")) { count += 1 }
            EButton(resource("Plain action"), emphasis: .plain) { count += 1 }
            EButton(resource("Destructive action"), role: .destructive) { count += 1 }
            EButton(resource("Disabled action"), action: {}).disabled(true)
            Text("Action count: \(count)", bundle: bundle).accessibilityIdentifier("playground.designkit.mac.button.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.icon-action

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/IconActionExample.swift`

# EIconAction

ID: designkit.mac.icon-action
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Use a named icon action when surrounding context makes its purpose clear.

## Capabilities
- Symbol or custom icon — systemImage, a ViewBuilder icon or a Text title with an icon.
- Role and busy — destructive role and isBusy behave like EButton.
- Accessible title — the required title is the accessibility name even though only the icon is visible.

## Parameters, state and constraints
Provide a meaningful title for VoiceOver and help. SF Symbols and custom image labels remain caller owned.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EIconAction

ID: designkit.mac.icon-action
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
上下文明确时使用有可访问名称的图标操作。

## 能力
- 符号或自定义图标 — 支持 systemImage、ViewBuilder 图标以及 Text 标题加图标。
- 角色与忙碌 — destructive 角色和 isBusy 与 EButton 一致。
- 可访问名称 — 必填 title 作为辅助功能名称，界面上只显示图标。

## 参数、状态与约束
必须提供可读的 VoiceOver/help 名称。SF Symbols 与自定义图片标签由调用方提供。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct IconActionExample: View {
    private let bundle: Bundle
    private let isBusy: Bool
    @State private var count = 0

    init(bundle: Bundle = .main, isBusy: Bool = false) {
        self.bundle = bundle
        self.isBusy = isBusy
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EIconAction(resource("Add item"), systemImage: "plus", isBusy: isBusy) { count += 1 }
                .accessibilityIdentifier("playground.designkit.mac.icon-action.trigger")
            EIconAction(resource("Custom icon"), action: { count += 1 }) { Image(systemName: "star") }
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.sheet-close-button

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/SheetCloseButtonExample.swift`

# ESheetCloseButton

ID: designkit.mac.sheet-close-button
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0
API available since: AppleAppKit 0.14.1

## Purpose
Dismiss a sheet with a compact, accessible close button.

## Capabilities
- Provides a 34 pt target around a 24 pt symbol disc.
- Supports Escape and a localized accessibility label.

## Parameters, state and constraints
Supply the localized label and a closure that dismisses the sheet. The host owns the presentation state.

# ESheetCloseButton

ID: designkit.mac.sheet-close-button
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0
API 起始版本：AppleAppKit 0.14.1

## 用途
在弹窗中提供带辅助功能名称的紧凑关闭按钮。

## 能力
- 24 pt 图形圆盘与 34 pt 点击区域。
- 支持 Escape 和本地化辅助功能名称。

## 参数、状态与约束
传入本地化名称和关闭回调，弹窗的展示状态由宿主持有。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct SheetCloseButtonExample: View {
    var bundle: Bundle = .main
    @State private var showsSheet = false

    var body: some View {
        Button { showsSheet = true } label: { Text("Show sheet", bundle: bundle) }
            .sheet(isPresented: $showsSheet) {
                ESheetCloseButton(Text("Close", bundle: bundle)) { showsSheet = false }
                    .padding()
            }
    }
}
#endif
```

## designkit.mac.menu

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/MenuExample.swift`

# EMenu

ID: designkit.mac.menu
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Present actions, grouped items and native toggle semantics.

## Capabilities
- Native menu — items, state marks and keyboard behavior are rendered by the system.
- Custom trigger — a ViewBuilder label supports icons or images; icon-only triggers need an accessibility label.
- Localized title — a LocalizedStringResource title builds a text trigger.

## Parameters, state and constraints
Opening or cancelling a menu must not execute actions. Do not nest a Button inside the trigger label or use this as a replacement for Picker.

Icons are optional and owned by the caller: use a native Button with a Label and SF Symbol for an icon, or Text for a text-only item. EMenu applies titleAndIcon to the native Menu as its default label strategy so supplied Label icons, including grouped and submenu items, remain visible on macOS 27; it does not invent icons for Text. Trigger labels follow the caller's Label or Text and can use a more local labelStyle override, such as iconOnly. Trigger and item labels remain independent: a text trigger can open icon items, and an icon-and-text trigger can open text items. Native selection marks, Toggle state, submenu arrows, disabled items and destructive roles stay with the system.

The fixture offers three triggers: text-only, icon items with a text trigger, and mixed grouped content with an icon-and-text trigger. The mixed menu also includes Toggle, a submenu, disabled and destructive actions. Stable trigger IDs end in menu.text-only, menu.with-icons and menu.trigger; actions update only the visible local count or Boolean Binding.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EMenu

ID: designkit.mac.menu
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
展示动作、分组条目和原生菜单勾选。

## 能力
- 原生菜单 — 菜单项、状态标记和键盘行为由系统渲染。
- 自定义触发器 — ViewBuilder 标签支持图标或图片，仅图标时需提供可访问标签。
- 本地化标题 — LocalizedStringResource 标题生成文字触发器。

## 参数、状态与约束
打开或取消菜单不执行动作。触发标签内不嵌套 Button，不把动作菜单替代 Picker。

图标由调用方按需提供：带图标的原生 Button 使用 Label 与 SF Symbol，纯文字项使用 Text。EMenu 在原生 Menu 上应用 titleAndIcon 作为默认标签策略，使 macOS 27 中调用方提供的 Label 图标（含分组和子菜单条目）保持显示；不会给 Text 凭空补图标。触发器按调用方的 Label 或 Text 展示，也可用更局部的 labelStyle（如 iconOnly）覆盖。触发器和条目标签互相独立：纯文字触发器可以打开图文条目，图文触发器也可以打开纯文字条目。系统勾选、Toggle 状态、子菜单箭头、禁用与危险角色均保留原生行为。

示例有三个触发器：纯文字菜单、纯文字触发但选项带图标的菜单，以及图文触发的分组混合菜单。混合菜单还包含 Toggle、子菜单、禁用和危险操作。稳定触发 ID 分别以 menu.text-only、menu.with-icons、menu.trigger 结尾；动作只更新可见局部计数或布尔 Binding。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct MenuExample: View {
    private let bundle: Bundle
    @State private var count = 0
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EMenu(resource("Text-only menu")) {
                Button { count += 1 } label: { Text("Run action", bundle: bundle) }
                Button {} label: { Text("Disabled action", bundle: bundle) }.disabled(true)
            }.accessibilityIdentifier("playground.designkit.mac.menu.text-only")
            EMenu(resource("Icon menu")) {
                Button { count += 1 } label: {
                    Label { Text("Run action", bundle: bundle) } icon: { Image(systemName: "play.fill") }
                }
                Button {} label: {
                    Label { Text("Disabled action", bundle: bundle) } icon: { Image(systemName: "eye.slash") }
                }.disabled(true)
                Button(role: .destructive) { count += 1 } label: {
                    Label { Text("Destructive action", bundle: bundle) } icon: { Image(systemName: "trash") }
                }
            }.accessibilityIdentifier("playground.designkit.mac.menu.with-icons")
            EMenu {
                Section {
                    Button { count += 1 } label: { Text("Run action", bundle: bundle) }
                    Button { count += 1 } label: {
                        Label { Text("Save", bundle: bundle) } icon: { Image(systemName: "square.and.arrow.down") }
                    }
                    Button {} label: { Text("Disabled action", bundle: bundle) }.disabled(true)
                } header: { Text("Actions", bundle: bundle) }
                Toggle(isOn: $enabled) {
                    Label { Text("Enabled", bundle: bundle) } icon: { Image(systemName: "bell") }
                }
                Menu {
                    Button { count += 1 } label: {
                        Label { Text("Retry", bundle: bundle) } icon: { Image(systemName: "arrow.clockwise") }
                    }
                    Button { count += 1 } label: { Text("Cancel", bundle: bundle) }
                } label: {
                    Label { Text("More actions", bundle: bundle) } icon: { Image(systemName: "folder") }
                }
                Divider()
                Button(role: .destructive) { count += 1 } label: { Text("Destructive action", bundle: bundle) }
            } label: {
                Label { Text("Mixed menu", bundle: bundle) } icon: { Image(systemName: "ellipsis.circle") }
            }.accessibilityIdentifier("playground.designkit.mac.menu.trigger")
            Text("Action count: \(count)", bundle: bundle).accessibilityIdentifier("playground.designkit.mac.menu.result")
            Text(enabled ? LocalizedStringKey("On") : LocalizedStringKey("Off"), bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.action-group

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ActionGroupExample.swift`

# EActionGroup

ID: designkit.mac.action-group
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Group related actions in content, toolbar or floating placement.

## Capabilities
- Grouped actions — lays out related buttons in one row with configurable spacing.
- Glass container — spacing also sets the glass merge threshold for floating buttons.
- Scope — for a few related actions only, not whole-page content.

## Parameters, state and constraints
The group does not own routes, keyboard shortcuts or task state. Floating uses a shared native glass sampling area.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EActionGroup

ID: designkit.mac.action-group
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
组合内容区、工具栏或浮动区域中的相关操作。

## 能力
- 操作组 — 把相关按钮排在一行，间距可配置。
- 玻璃容器 — spacing 同时决定浮动按钮的玻璃合并阈值。
- 范围 — 只用于少量相关操作，不包裹整页内容。

## 参数、状态与约束
不拥有路由、快捷键或任务状态。浮动场景共享原生玻璃采样区域。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ActionGroupExample: View {
    private let bundle: Bundle
    private let isBusy: Bool
    @State private var count = 0

    init(bundle: Bundle = .main, isBusy: Bool = false) {
        self.bundle = bundle
        self.isBusy = isBusy
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EActionGroup {
                EButton(resource("Cancel")) { count += 1 }
                EButton(resource("Save"), emphasis: .primary, isBusy: isBusy) { count += 1 }
            }
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.picker

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/PickerExample.swift`

# EPicker

ID: designkit.mac.picker
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Choose a strongly typed or Optional value through a native menu or segments.

## Capabilities
- Menu presentation — the default pop-up menu that shows only the selected value.
- Segmented presentation — EPickerPresentation.segmented for a few mutually exclusive options.
- Typed selection — options carry tags that match the Selection type; disabled items are kept.
- Selected label — selectedLabel and maxLabelWidth shorten the collapsed label without trimming the menu.

## Parameters, state and constraints
Tags must match the Binding type. A removed candidate does not select the first item; provide nil or an identifiable unmatched state. The fixture exposes raw selection.

Menu option icons are optional: Label with an SF Symbol supplies an icon, while Text remains text-only. EPicker applies titleAndIcon only in its menu branch, including on macOS 27, without changing the native checkmark, menu arrow, tag or Binding semantics. The trigger title does not determine whether options have icons. Segmented presentation keeps its existing native styling and is not given the menu-only label-style override.

The fixture combines a text-only nil option, icon options, a disabled icon option and a dynamic text option, all with stable Optional String tags. Its segmented example remains text-only, and both actual selections are visible below the controls.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EPicker

ID: designkit.mac.picker
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
通过原生菜单或分段选择强类型或 Optional 值。

## 能力
- 菜单呈现 — 默认弹出菜单，收起时只显示当前值。
- 分段呈现 — EPickerPresentation.segmented 适合少量互斥选项。
- 强类型选择 — 选项 tag 与 Selection 类型一致，保留禁用项语义。
- 选中标签 — selectedLabel 与 maxLabelWidth 只缩短收起状态的标签，不影响菜单内完整选项。

## 参数、状态与约束
tag 必须与 Binding 类型匹配。候选移除不自动改选第一项；提供 nil 或明确未匹配状态。示例显示实际选值。

菜单选项图标可选：Label 与 SF Symbol 提供图标，Text 继续显示纯文字。EPicker 仅在 menu 分支应用 titleAndIcon，使 macOS 27 也显式显示所提供的图标，不改变原生勾选、菜单箭头、tag 或 Binding 语义。触发器标题不决定选项是否带图标。分段呈现保留原样，不套用菜单专属的标签样式覆盖。

示例把纯文字 nil 选项、图文选项、带图标的禁用项和动态纯文字项放在同一菜单，均使用稳定 Optional String tag。分段示例保持纯文字；两个控件的实际选值均在下方可见。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct PickerExample: View {
    private let bundle: Bundle
    private let isEmpty: Bool
    @State private var selected: String? = nil
    @State private var segment = 0
    @State private var includeOption = true

    init(bundle: Bundle = .main, isEmpty: Bool = false) {
        self.bundle = bundle
        self.isEmpty = isEmpty
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EPicker(resource("Choose an option"), selection: $selected) {
                Text("No selection", bundle: bundle).tag(nil as String?)
                if !isEmpty {
                    Label { Text("First option", bundle: bundle) } icon: { Image(systemName: "star") }
                        .tag("first" as String?)
                    Label { Text("Disabled option", bundle: bundle) } icon: { Image(systemName: "lock") }
                        .tag("disabled" as String?).disabled(true)
                    if includeOption { Text("Dynamic option", bundle: bundle).tag("dynamic" as String?) }
                }
            }.accessibilityIdentifier("playground.designkit.mac.picker.menu")
            ECheckbox(resource("Include dynamic option"), isOn: $includeOption)
            EPicker(resource("Segment"), selection: $segment, presentation: .segmented) {
                Text("First", bundle: bundle).tag(0)
                Text("Second", bundle: bundle).tag(1)
            }.accessibilityIdentifier("playground.designkit.mac.picker.segment")
            Text(verbatim: selected ?? "nil").accessibilityIdentifier("playground.designkit.mac.picker.selection")
            Text("Selected segment: \(segment)", bundle: bundle).accessibilityIdentifier("playground.designkit.mac.picker.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.switch

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/SwitchExample.swift`

# ESwitch

ID: designkit.mac.switch
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Express an immediate Boolean preference using a native switch.

## Capabilities
- Binary setting — binds to a Bool and uses the native switch style.
- Accessible title — the title is the accessibility name; hide the visual label with labelsHidden when needed.
- Rich title — accepts LocalizedStringResource or a Text that keeps bundle and verbatim semantics.

## Parameters, state and constraints
Binding is selection, not proof of remote persistence. Preserve an accessible label even when labelsHidden is used.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ESwitch

ID: designkit.mac.switch
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
用原生开关表达即时布尔选择。

## 能力
- 二态设置 — 绑定 Bool，采用原生开关样式。
- 可访问标题 — title 即辅助功能名称，需要隐藏视觉标签时用 labelsHidden。
- 标题形式 — 支持 LocalizedStringResource，或保留 bundle 与 verbatim 语义的 Text。

## 参数、状态与约束
Binding 表示选择，不表示远端保存成功。隐藏视觉标签后仍须保留可访问名称。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SwitchExample: View {
    private let bundle: Bundle
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ESwitch(resource("Enabled"), isOn: $enabled).accessibilityIdentifier("playground.designkit.mac.switch.control")
            EButton(resource("Change externally")) { enabled.toggle() }
            Text(enabled ? LocalizedStringKey("On") : LocalizedStringKey("Off"), bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.checkbox

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/CheckboxExample.swift`

# ECheckbox

ID: designkit.mac.checkbox
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Express a desktop Boolean choice using a native checkbox.

## Capabilities
- Binary choice — binds to a Bool with the native checkbox style.
- Accessible title — the title doubles as the accessibility name even when the visual label is hidden.
- Rich title — accepts LocalizedStringResource or Text.

## Parameters, state and constraints
Do not use the checkbox to impersonate switch presentation or menu state; network confirmation stays with the caller.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ECheckbox

ID: designkit.mac.checkbox
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
用原生桌面复选框表达布尔选择。

## 能力
- 二态选择 — 绑定 Bool，采用原生复选框样式。
- 可访问标题 — 即使隐藏视觉标签，标题仍是辅助功能名称。
- 标题形式 — 支持 LocalizedStringResource 或 Text。

## 参数、状态与约束
不要冒充开关外观或菜单状态；网络确认由宿主处理。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct CheckboxExample: View {
    private let bundle: Bundle
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ECheckbox(resource("Remember this choice"), isOn: $enabled).accessibilityIdentifier("playground.designkit.mac.checkbox.control")
            EButton(resource("Change externally")) { enabled.toggle() }
            Text(enabled ? LocalizedStringKey("On") : LocalizedStringKey("Off"), bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.text-field

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/TextFieldExample.swift`

# ETextField

ID: designkit.mac.text-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Edit a single line while preserving native input, submit and focus behavior.

## Capabilities
- Single-line text — plain text field inside the shared field chrome.
- Title as placeholder — the title is both placeholder and accessibility name.
- Rich title — accepts LocalizedStringResource or Text.

## Parameters, state and constraints
No trim, case conversion, history or business validation occurs. The fixture displays verbatim Binding text and a submit count; marked text must remain intact.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ETextField

ID: designkit.mac.text-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
编辑单行文本，保留原生输入、提交与焦点行为。

## 能力
- 单行文本 — 在统一字段外观内的纯文本输入。
- 标题即占位 — title 同时是占位文字和辅助功能名称。
- 标题形式 — 支持 LocalizedStringResource 或 Text。

## 参数、状态与约束
不裁剪空白、不改大小写、不保存历史、不执行业务校验。示例显示 Binding 原文与提交次数；输入法组合文本必须保留。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct TextFieldExample: View {
    private let bundle: Bundle
    @State private var value = "  original text  "
    @State private var submits = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ETextField(resource("Name"), text: $value)
                .onSubmit { submits += 1 }.accessibilityIdentifier("playground.designkit.mac.text-field.input")
            Text(verbatim: value).textSelection(.enabled).accessibilityIdentifier("playground.designkit.mac.text-field.result")
            Text("Submit count: \(submits)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.secure-field

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/SecureFieldExample.swift`

# ESecureField

ID: designkit.mac.secure-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Edit a password using the native secure editor.

## Capabilities
- Masked input — secure text entry inside the shared field chrome.
- No validation — strength and match rules belong to the caller.
- Rich title — accepts LocalizedStringResource or Text.

## Parameters, state and constraints
Never replace it with TextField to reveal content or log the Binding. The fixture shows only a character count, not the password. AutoFill needs foreground verification.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ESecureField

ID: designkit.mac.secure-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
使用原生安全编辑器输入密码。

## 能力
- 密文输入 — 在统一字段外观内的安全文本输入。
- 不做校验 — 强度和一致性规则由调用方负责。
- 标题形式 — 支持 LocalizedStringResource 或 Text。

## 参数、状态与约束
不替换成 TextField 展示密码，不记录 Binding。示例仅显示字数，不显示密码。AutoFill 需要前台验证。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SecureFieldExample: View {
    private let bundle: Bundle
    @State private var password = ""
    @State private var submits = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ESecureField(resource("Password"), text: $password).textContentType(.newPassword)
                .onSubmit { submits += 1 }.accessibilityIdentifier("playground.designkit.mac.secure-field.input")
            Text("Character count: \(password.count)", bundle: bundle)
            Text("Submit count: \(submits)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.search-field

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/SearchFieldExample.swift`

# ESearchField

ID: designkit.mac.search-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Edit and clear the current search Binding.

## Capabilities
- Search chrome — uses the taller searchHeight from the theme.
- Clear action — requires a localized clearTitle for the clear button's accessibility name.
- Rich title — accepts LocalizedStringResource or Text.

## Parameters, state and constraints
Clear removes only the current text. The component never deletes history, starts a network request or implicitly submits.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ESearchField

ID: designkit.mac.search-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
编辑并清空当前搜索 Binding。

## 能力
- 搜索外观 — 使用主题中更高的 searchHeight。
- 清除操作 — 必须提供本地化 clearTitle 作为清除按钮的辅助功能名称。
- 标题形式 — 支持 LocalizedStringResource 或 Text。

## 参数、状态与约束
清空仅影响当前文本，不删除历史、不发网络请求、不隐式提交。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SearchFieldExample: View {
    private let bundle: Bundle
    @State private var query = "Alpha"

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ESearchField(resource("Search"), text: $query, clearTitle: resource("Clear search"))
                .accessibilityIdentifier("playground.designkit.mac.search-field.input")
            Text(verbatim: query).accessibilityIdentifier("playground.designkit.mac.search-field.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.combo-box

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ComboBoxExample.swift`

# EComboBox

ID: designkit.mac.combo-box
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Edit raw text with native NSComboBox suggestions and explicit submission.

## Capabilities
- Editable suggestions — native combo box with free text and a suggestion list.
- Commit semantics — onCommit runs only on commit; cancel, close and focus loss never call it.
- Optional focus binding — isFocused exposes focus to the caller.
- Verbatim title — init(verbatim:) for runtime strings that must not be localization keys.

## Parameters, state and constraints
Suggestions are raw strings, deduplicated by text. Use a typed Picker for distinct objects with equal names. Editing-ended differs from commit; IME, keyboard and pop-up edges need foreground acceptance.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

The native ComboBox uses EControlTheme.typography.nativeBodySize. The local larger-text preview updates both this native size and SwiftUI body typography. Actual glyph metrics, IME composition and focus still require foreground verification.

# EComboBox

ID: designkit.mac.combo-box
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
用原生 NSComboBox 建议编辑原文并明确提交。

## 能力
- 可编辑候选 — 原生组合框，支持自由输入和候选列表。
- 提交语义 — 只有提交才调用 onCommit，取消、关闭和失焦都不调用。
- 可选焦点绑定 — isFocused 向调用方暴露焦点。
- 原文标题 — init(verbatim:) 用于不能当作本地化 key 的运行时字符串。

## 参数、状态与约束
候选为按文本去重的原文。同名不同对象用强类型 Picker。编辑结束不等于提交；输入法、键盘和弹出边缘需要前台验收。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

原生 ComboBox 使用 EControlTheme.typography.nativeBodySize。本页放大预览同时更新该原生字号与 SwiftUI 正文排版。实际字形度量、输入法组合与焦点仍须前台验证。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ComboBoxExample: View {
    private let bundle: Bundle
    private let isEmpty: Bool
    @State private var value = ""
    @State private var suggestions = ["Alpha", "Bravo", "中文输入", "Alpha"]
    @State private var submits = 0
    @State private var editingEnds = 0

    init(bundle: Bundle = .main, isEmpty: Bool = false) {
        self.bundle = bundle
        self.isEmpty = isEmpty
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EComboBox(resource("Suggestions"), text: $value, suggestions: isEmpty ? [] : suggestions,
                      onEditingEnded: { _ in editingEnds += 1 }) { _ in submits += 1 }
                .accessibilityIdentifier("playground.designkit.mac.combo-box.input")
            EActionGroup {
                EButton(resource("Reverse options")) { suggestions.reverse() }
                EButton(resource("Remove options")) { suggestions = [] }
                EButton(resource("Restore options")) { suggestions = ["Alpha", "Bravo", "中文输入", "Alpha"] }
            }
            Text(verbatim: value).accessibilityIdentifier("playground.designkit.mac.combo-box.result")
            Text("Submit count: \(submits)", bundle: bundle)
            Text("Editing ended: \(editingEnds)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.field

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/FieldExample.swift`

# EField

ID: designkit.mac.field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Combine a label, editor, hint and validation error.

## Capabilities
- Label and hint — wraps any input with a title and optional hint text.
- Error state — an error message replaces the hint and is shown in the danger color.
- Any content — works with EFieldShell inputs and native controls.

## Parameters, state and constraints
Error replaces hint without changing input or focus. The caller owns validation and provides an editor with the correct accessible title.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EField

ID: designkit.mac.field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
组合标签、编辑器、说明与校验错误。

## 能力
- 标签与提示 — 给任意输入加标题和可选提示文字。
- 错误状态 — error 文案取代提示，并以危险色显示。
- 任意内容 — 可包裹 EFieldShell 输入或原生控件。

## 参数、状态与约束
错误优先显示，但不改输入或焦点。校验由宿主负责，编辑器必须有正确的可访问标题。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct FieldExample: View {
    private let bundle: Bundle
    private let isInvalid: Bool
    @State private var value = ""

    init(bundle: Bundle = .main, isInvalid: Bool = false) {
        self.bundle = bundle
        self.isInvalid = isInvalid
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EField(resource("Name"), hint: resource("Whitespace and marked text are preserved"),
                   error: isInvalid ? resource("Review this long validation message and correct the value without losing your input") : nil) {
                ETextField(resource("Name"), text: $value).accessibilityIdentifier("playground.designkit.mac.field.input")
            }
            Text(verbatim: value)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.field-shell

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/FieldShellExample.swift`

# EFieldShell

ID: designkit.mac.field-shell
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Apply the field appearance to a native editor that requires direct focus or input configuration.

## Capabilities
- Shared chrome — surface fill, separator stroke and field radius from the theme.
- Search variant — isSearch switches to the search height.
- Content-sized — minimum height only, content is never clipped.

## Parameters, state and constraints
The slot keeps the native editor and its input contract. The shell does not own focus, submit, validation or data transformation.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EFieldShell

ID: designkit.mac.field-shell
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
为需要直接配置焦点或输入行为的原生编辑器复用字段外观。

## 能力
- 统一外观 — 填充、分隔线描边和字段圆角都来自主题。
- 搜索变体 — isSearch 切换到搜索高度。
- 随内容增长 — 只设最小高度，不裁剪内容。

## 参数、状态与约束
保留原生编辑器及输入契约。外壳不拥有焦点、提交、校验或数据转换。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 原生复杂编辑器复用外壳，输入行为和焦点仍由编辑器拥有。
struct FieldShellExample: View {
    private let bundle: Bundle
    @State private var value = ""
    @FocusState private var focused: Bool

    init(bundle: Bundle = .main) { self.bundle = bundle }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EFieldShell {
                TextField(text: $value) { Text("Name", bundle: bundle) }
                    .textFieldStyle(.plain)
                    .focused($focused)
                    .accessibilityIdentifier("playground.designkit.mac.field-shell.input")
            }
            EButton(LocalizedStringResource("Focus input", bundle: .atURL(bundle.bundleURL))) { focused = true }
            Text(verbatim: value)
        }
    }
}
#endif
```

## designkit.mac.card

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/CardExample.swift`

# ECard

ID: designkit.mac.card
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Group content on a semantic opaque surface.

## Capabilities
- Surface container — theme surface fill with the card radius and card inset.
- Full width — stretches to the available width, content aligned leading.
- No navigation or glass — the card does not own navigation or glass effects.

## Parameters, state and constraints
A content card is not a glass control or a navigation action. Supply any actions explicitly.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ECard

ID: designkit.mac.card
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
在语义实色背景上组织内容。

## 能力
- 表面容器 — 主题表面色、卡片圆角和卡片内边距。
- 撑满宽度 — 填满可用宽度，内容靠前对齐。
- 不含导航和玻璃 — 卡片不拥有导航或玻璃效果。

## 参数、状态与约束
内容卡不是玻璃控件或导航动作；操作必须明确提供。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct CardExample: View {
    private let bundle: Bundle
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        ECard {
            VStack(alignment: .leading, spacing: 12) {
                Text("Content card", bundle: bundle).font(.headline)
                Text("Cards do not own navigation or glass effects", bundle: bundle)
                EButton(resource("Run action")) { count += 1 }
                Text("Action count: \(count)", bundle: bundle)
            }
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.settings-row

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/SettingsRowExample.swift`

# ESettingsRow

ID: designkit.mac.settings-row
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Pair a label and explanation with a native setting control.

## Capabilities
- Title and detail — a title with optional secondary detail text.
- Trailing control — any control (switch, picker, button) placed on the trailing side.
- Natural growth — long text wraps and the row grows instead of truncating.

## Parameters, state and constraints
The row adapts to narrow space without a fixed height. The caller owns selection and persistence; the row adds no tap or navigation behavior.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ESettingsRow

ID: designkit.mac.settings-row
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
把标签、说明和原生设置控件放在同一行。

## 能力
- 标题与说明 — 标题加可选的次要说明。
- 尾部控件 — 可在右侧放任意控件（开关、选择器、按钮）。
- 自然增高 — 长文本换行并增高，不截断。

## 参数、状态与约束
窄空间自适应，不固定高度。选择和持久化由宿主负责；行本身不添加点击或导航行为。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SettingsRowExample: View {
    private let bundle: Bundle
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        ESettingsRow(resource("Background work"), detail: resource("This long explanation wraps and the control moves below the title when space is limited")) {
            ESwitch(resource("Enabled"), isOn: $enabled).labelsHidden()
                .accessibilityIdentifier("playground.designkit.mac.settings-row.control")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.label-value

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/LabelValueExample.swift`

# ELabelValue

ID: designkit.mac.label-value
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Display a readable, selectable static value next to its meaning.

## Capabilities
- Read-only pair — a title and a value laid out like a settings row.
- Selectable value — the value text can be selected and copied.
- Text values — the value is a Text so it keeps localization or verbatim semantics.

## Parameters, state and constraints
Use Text(verbatim:) for user or protocol content. Formatting and confidentiality belong to the caller.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ELabelValue

ID: designkit.mac.label-value
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
展示可读可选择的标签值。

## 能力
- 只读键值 — 标题与值按设置行样式排列。
- 值可选中 — 值文字可选中复制。
- Text 值 — 值为 Text，保留本地化或 verbatim 语义。

## 参数、状态与约束
用户或协议原文使用 Text(verbatim:)。格式化与保密由宿主负责。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct LabelValueExample: View {
    private let bundle: Bundle
    @State private var value = "  example.original  "

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ETextField(resource("Original text"), text: $value)
            ELabelValue(resource("Value"), value: Text(verbatim: value))
                .accessibilityIdentifier("playground.designkit.mac.label-value.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.text

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/TextExample.swift`

# EText

ID: designkit.mac.text
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Show text with a semantic role (body, secondary, caption, title, section title, page title, monospaced) instead of raw system fonts and .secondary colors.

## Capabilities
- Seven roles — body, secondary, caption, title, sectionTitle, pageTitle and monospaced.
- Tone override — tone (EStatusTone) replaces the role color for status text.
- Modifier form — .eText(_:tone:) applies a role to Label or any view.
- Three initializers — Text, LocalizedStringResource and verbatim.

## Parameters, state and constraints
Fonts come from ETypography and colors from ESemanticColors through the injected eControlTheme. tone reuses EStatusTone and overrides the role color; status must still carry readable text. .eText(_:tone:) applies the same role to Label or any other view.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EText

ID: designkit.mac.text
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
按语义角色（正文、次要、脚注、标题、分组标题、页面标题、等宽）展示文本，取代裸写系统字体与 .secondary。

## 能力
- 七种角色 — body、secondary、caption、title、sectionTitle、pageTitle、monospaced。
- 语义色覆盖 — tone（EStatusTone）覆盖角色颜色，用于状态文字。
- 修饰符形式 — .eText(_:tone:) 可套在 Label 或任意视图上。
- 三种初始化 — Text、LocalizedStringResource 和 verbatim。

## 参数、状态与约束
字体读 ETypography，颜色读 ESemanticColors，均来自注入的 eControlTheme。tone 复用 EStatusTone 并覆盖角色颜色，状态仍须配有可读文字。.eText(_:tone:) 可用于 Label 等任意视图。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct TextExample: View {
    private let bundle: Bundle

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            EText(resource("Page title"), role: .pageTitle)
            EText(resource("Section title"), role: .sectionTitle)
            EText(resource("Body text"), role: .body)
            EText(resource("Secondary text"), role: .secondary)
            EText(resource("Caption text"), role: .caption)
            EText(verbatim: "/Users/example/file.txt", role: .monospaced)
            EText(resource("Failed"), role: .caption, tone: .failure)
            Label("Label with role", systemImage: "tag").eText(.secondary)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.status-badge

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/StatusBadgeExample.swift`

# EStatusBadge

ID: designkit.mac.status-badge
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Present neutral, success, warning and failure with text plus an icon.

## Capabilities
- Four tones — neutral, success, warning and failure, each with its own SF Symbol.
- Text plus icon — status never relies on color alone.
- Compact — caption font for inline status.

## Parameters, state and constraints
The badge does not infer business success and is not an action. Never rely on color alone or replace danger with brand accent.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EStatusBadge

ID: designkit.mac.status-badge
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
通过文字和图标展示普通、成功、警告与失败状态。

## 能力
- 四种语义 — neutral、success、warning、failure，各有对应 SF Symbol。
- 文字加图标 — 状态不只靠颜色区分。
- 紧凑 — 使用说明字号，适合行内状态。

## 参数、状态与约束
不推断业务成功，也不是按钮。不仅依赖颜色，不把危险色替换成品牌强调色。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct StatusBadgeExample: View {
    private let bundle: Bundle

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EStatusBadge(resource("Information"), tone: .neutral)
            EStatusBadge(resource("Succeeded"), tone: .success)
            EStatusBadge(resource("Warning"), tone: .warning)
            EStatusBadge(resource("Failed"), tone: .failure)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.content-state

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ContentStateExample.swift`

# EContentState

ID: designkit.mac.content-state
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Present an explicit idle, loading, empty, failure or success result.

## Capabilities
- Five phases — idle, loading, empty, failure and success.
- Title, detail and symbol — optional detail text and SF Symbol.
- Actions slot — a ViewBuilder for retry or follow-up actions.

## Parameters, state and constraints
The caller supplies phase and retry actions. Empty data is not proof of success or loading; no automatic retry occurs.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EContentState

ID: designkit.mac.content-state
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
展示明确的空闲、加载、空内容、失败或成功结果。

## 能力
- 五种阶段 — idle、loading、empty、failure、success。
- 标题、说明与符号 — 可选说明文字和 SF Symbol。
- 操作插槽 — ViewBuilder 可放重试等后续操作。

## 参数、状态与约束
阶段和重试动作由宿主提供。空数据不能推断成功或加载；不自动重试。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ContentStateExample: View {
    private let bundle: Bundle
    @State private var phase = 0
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EPicker(resource("Content state"), selection: $phase) {
                Text("Idle", bundle: bundle).tag(0)
                Text("Loading", bundle: bundle).tag(1)
                Text("Empty", bundle: bundle).tag(2)
                Text("Failed", bundle: bundle).tag(3)
                Text("Succeeded", bundle: bundle).tag(4)
            }
            EContentState(currentPhase, title: resource("Explicit content state"), detail: resource("The caller owns the result and retry decision")) {
                EButton(resource("Retry")) { count += 1 }
            }
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private var currentPhase: EContentPhase {
        switch phase {
        case 0: .idle
        case 1: .loading
        case 2: .empty
        case 3: .failure
        default: .success
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.notice

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/NoticeExample.swift`

# ENotice

ID: designkit.mac.notice
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Keep important information or failure readable until replaced by the caller.

## Capabilities
- Tones — neutral, success, warning and failure.
- Adaptive layout — actions sit beside the text when wide and wrap below when narrow.
- Actions slot — optional ViewBuilder actions such as dismiss or retry.

## Parameters, state and constraints
Persistent and non-modal. Actions remain explicit and do not disable unrelated controls.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ENotice

ID: designkit.mac.notice
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
保留重要信息或错误，直到宿主主动更新。

## 能力
- 语义 — neutral、success、warning、failure。
- 自适应布局 — 宽时操作在文字旁，窄时换到下方。
- 操作插槽 — 可选的 ViewBuilder 操作，如关闭或重试。

## 参数、状态与约束
持续、非模态。操作必须明确提供，不禁用无关控件。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct NoticeExample: View {
    private let bundle: Bundle
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ENotice(resource("This important error remains until the caller replaces it"), tone: .failure) {
                EButton(resource("Review details")) { count += 1 }
            }
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.toast

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ToastExample.swift`

# EToast

ID: designkit.mac.toast
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Show brief non-critical success feedback from an external message Binding.

## Capabilities
- Transient message — bound to an EToastMessage? and cleared automatically.
- Auto dismiss — dismissAfter defaults to two seconds; replacing the message restarts the timer.
- Verbatim or localized — EToastMessage(verbatim:) for runtime text.
- Announcement — the message is announced to assistive technology; dismissTitle names the dismiss action.

## Parameters, state and constraints
Two-second dismissal pauses for hover, focus and VoiceOver; replacements and teardown cancel old work. Important failures belong in ENotice. Each repeated message has a new identity.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EToast

ID: designkit.mac.toast
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
通过外部消息 Binding 展示简短非关键成功提示。

## 能力
- 短暂消息 — 绑定 EToastMessage?，自动清除。
- 自动消失 — dismissAfter 默认两秒，替换消息会重新计时。
- 原文或本地化 — 运行时文字用 EToastMessage(verbatim:)。
- 公告 — 消息会向辅助技术播报，dismissTitle 为关闭动作命名。

## 参数、状态与约束
两秒计时在悬停、焦点或 VoiceOver 时暂停；替换和销毁取消旧任务。重要失败使用 ENotice。相同文字的再次消息也有新身份。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ToastExample: View {
    private let bundle: Bundle
    @State private var message: EToastMessage?
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EActionGroup {
                EButton(resource("Show success")) { count += 1; message = EToastMessage(resource("Action completed")) }
                EButton(resource("Replace message")) { count += 1; message = EToastMessage(resource("Saved")) }
                EButton(resource("Clear message")) { message = nil }
            }
            EToast(message: $message, dismissTitle: resource("Dismiss notice"))
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.task-progress

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/TaskProgressExample.swift`

# ETaskProgress

ID: designkit.mac.task-progress
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Display determinate or indeterminate external task progress and explicit actions.

## Capabilities
- Determinate progress — EProgressFraction accepts only finite values within 0 to 1.
- Indeterminate progress — a nil fraction shows an indeterminate indicator.
- Explicit actions — cancel or other actions are supplied in the actions slot.

## Parameters, state and constraints
Validate finite fractions in 0...1 with EProgressFraction. Requesting cancellation is not completion; the fixture waits for a separate confirmation and starts no real task.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# ETaskProgress

ID: designkit.mac.task-progress
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
展示外部任务的定量或不定量进度与明确操作。

## 能力
- 确定进度 — EProgressFraction 只接受 0 到 1 的有限值。
- 不确定进度 — fraction 为 nil 时显示不确定指示。
- 显式操作 — 取消等操作由 actions 插槽提供。

## 参数、状态与约束
用 EProgressFraction 校验有限的 0...1 数值。请求取消不等于取消完成；示例等待独立确认，不启动真实任务。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct TaskProgressExample: View {
    private let bundle: Bundle
    @State private var fraction = 0.4
    @State private var cancelRequested = false
    @State private var cancelled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if cancelled {
                EStatusBadge(resource("Cancelled"), tone: .neutral)
            } else if let progress = EProgressFraction(fraction) {
                ETaskProgress(resource("Transferring"), fraction: progress) {
                    EButton(resource("Cancel task")) { cancelRequested = true }.disabled(cancelRequested)
                }
            } else {
                ENotice(resource("Invalid progress"), tone: .failure)
            }
            Slider(value: $fraction, in: 0...1)
            if cancelRequested { Text("Cancellation requested; waiting for confirmation", bundle: bundle) }
            EButton(resource("Confirm cancellation")) { cancelled = true }
            ETaskProgress(resource("Preparing"))
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.form

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/FormExample.swift`

# EForm

ID: designkit.mac.form
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Keep form content scrollable while its action area remains reachable.

## Capabilities
- Content plus actions — two slots: fields on top, action buttons below.
- Group spacing — spacing comes from the theme group role.
- State owned by caller — validation and submit state are passed in by the host.

## Parameters, state and constraints
The host owns validation, Enter/Escape behavior, save and cancel. Avoid nesting an unbounded full-page form in another fixed-height form.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

# EForm

ID: designkit.mac.form
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
表单正文可滚动，动作区始终可达。

## 能力
- 内容与操作 — 两个插槽：上方字段，下方操作按钮。
- 分组间距 — 间距来自主题 group 角色。
- 状态由调用方持有 — 校验和提交状态由宿主传入。

## 参数、状态与约束
宿主拥有校验、Enter/Escape、保存和取消。避免在固定高度表单中再嵌无界整页表单。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct FormExample: View {
    private let bundle: Bundle
    private let isBusy: Bool
    private let isInvalid: Bool
    @State private var value = ""
    @State private var count = 0

    init(bundle: Bundle = .main, isBusy: Bool = false, isInvalid: Bool = false) {
        self.bundle = bundle
        self.isBusy = isBusy
        self.isInvalid = isInvalid
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EForm {
                EField(resource("Name"), error: isInvalid ? resource("Name is required") : nil) {
                    ETextField(resource("Name"), text: $value)
                }
                Text("Long form content remains scrollable while actions stay reachable", bundle: bundle)
                ETextField(resource("Read only"), text: .constant("Original value")).disabled(true)
            } actions: {
                EActionGroup {
                    EButton(resource("Cancel")) { count += 1 }
                    EButton(resource("Save"), emphasis: .primary, isBusy: isBusy) { count += 1 }
                }
            }.frame(height: 240)
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
```

## designkit.mac.page-header

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/PageHeaderExample.swift`

# PageHeaderExample

ID: designkit.mac.page-header
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Shared page heading and supporting text.

## Capabilities
- Title and subtitle — page title font with an optional secondary subtitle.
- Text inputs — title and subtitle are Text, keeping localization semantics.

# PageHeaderExample

ID: designkit.mac.page-header
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

共享页头与说明。

## 能力
- 标题与副标题 — 页面标题字体加可选次要副标题。
- Text 输入 — 标题和副标题是 Text，保留本地化语义。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct PageHeaderExample: View {
    var body: some View {
        EPageHeader(title: Text("Settings"), subtitle: Text("Shared page heading"))
    }
}
#endif
```

## designkit.mac.settings-page

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/SettingsPageExample.swift`

# SettingsPageExample

ID: designkit.mac.settings-page
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Shared page insets and scrolling.

## Capabilities
- Page scaffold — scrollable page with the standard inset and section spacing.
- Max content width — maxContentWidth limits line length on wide windows.

# SettingsPageExample

ID: designkit.mac.settings-page
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

统一页内留白与滚动。

## 能力
- 页面骨架 — 带标准边距和分区间距的可滚动页面。
- 最大内容宽度 — maxContentWidth 限制宽窗口下的行长。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct SettingsPageExample: View {
    var body: some View {
        ESettingsPage { EPageHeader(title: Text("Settings")); ETextField("Name", text: .constant("Example")) }.frame(height: 220)
    }
}
#endif
```

## designkit.mac.item-row

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ItemRowExample.swift`

# ItemRowExample

ID: designkit.mac.item-row
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Shared row hover, selection and action layout.

## Capabilities
- Selected state — isSelected draws the accent selection wash.
- Free content — any horizontal content with standard row padding.

# ItemRowExample

ID: designkit.mac.item-row
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

共享行的悬停、选中与操作布局。

## 能力
- 选中状态 — isSelected 绘制强调色选中底色。
- 自由内容 — 任意横向内容，带标准行边距。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct ItemRowExample: View {
    var body: some View {
        EItemRow { Label("Action", systemImage: "doc"); Spacer(); ESwitch("Enabled", isOn: .constant(true)) }
    }
}
#endif
```

## designkit.mac.sidebar-item

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/SidebarItemExample.swift`

# SidebarItemExample

ID: designkit.mac.sidebar-item
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Shared sidebar item layout.

## Capabilities
- Sidebar row — body font, minimum field height and standard vertical padding.
- Free content — label, icon and trailing accessories are supplied by the caller.

# SidebarItemExample

ID: designkit.mac.sidebar-item
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

共享侧栏项目布局。

## 能力
- 侧栏行 — 正文字体、最小字段高度和标准纵向内边距。
- 自由内容 — 标签、图标和尾部附件由调用方提供。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct SidebarItemExample: View {
    var body: some View {
        ESidebarItem { Label("Files", systemImage: "folder") }
    }
}
#endif
```

## designkit.mac.application-icon

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ApplicationIconExample.swift`

# ApplicationIconExample

ID: designkit.mac.application-icon
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Local application icons with an explicit missing-app symbol.

## Capabilities
- Installed app icon — resolved from a bundle identifier through Launch Services.
- Custom path — appPath covers apps not yet registered.
- Fallback symbol — a required SF Symbol is shown when the app cannot be found.

# ApplicationIconExample

ID: designkit.mac.application-icon
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

读取本机应用图标，缺失时显示指定符号。

## 能力
- 已安装应用图标 — 按 Bundle ID 通过 Launch Services 解析。
- 自定义路径 — appPath 覆盖尚未注册的应用。
- 回退符号 — 找不到应用时显示必填的 SF Symbol。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct ApplicationIconExample: View {
    var body: some View {
        EApplicationIcon(bundleIdentifier: "com.apple.Terminal", fallbackSymbol: "terminal")
    }
}
#endif
```

## designkit.mac.progress-panel-content

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ProgressPanelContentExample.swift`

# ProgressPanelContentExample

ID: designkit.mac.progress-panel-content
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Task progress and actions without owning the task.

## Capabilities
- Title, progress and hint — a title, optional EProgressFraction and optional hint text.
- Actions slot — cancel or close actions are supplied by the caller.

# ProgressPanelContentExample

ID: designkit.mac.progress-panel-content
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

任务进度与操作区；不执行任务。

## 能力
- 标题、进度与提示 — 标题、可选 EProgressFraction 和可选提示文字。
- 操作插槽 — 取消或关闭操作由调用方提供。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct ProgressPanelContentExample: View {
    var body: some View {
        EProgressPanelContent(title: Text("Processing"), hint: Text("Cancellation is handled by the host.")) { EButton("Cancel", action: {}) }
    }
}
#endif
```

## designkit.mac.reorderable-list

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ReorderableListExample.swift`

# ReorderableListExample

ID: designkit.mac.reorderable-list
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Shared reorder interactions with host-owned persistence.

## Capabilities
- Native drag reorder — rows move through the system reorder gesture.
- Keyboard-accessible moves — moveUpLabel and moveDownLabel name the accessibility actions.
- Caller persistence — onMove decides whether a move is accepted; saving is the caller's job.

# ReorderableListExample

ID: designkit.mac.reorderable-list
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

排序交互由组件管理，顺序保存由宿主负责。

## 能力
- 原生拖拽排序 — 行通过系统排序手势移动。
- 可访问的移动 — moveUpLabel 和 moveDownLabel 为辅助功能操作命名。
- 调用方持久化 — onMove 决定是否接受移动，保存由调用方负责。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct ReorderableListExample: View {
    private struct Entry: Identifiable { let id: String }
    var body: some View {
        EReorderableList(items: [Entry(id: "one"), Entry(id: "two")], reorderLabel: "Reorder", moveUpLabel: "Move up", moveDownLabel: "Move down", onMove: { _, _ in false }) { Text($0.id) }.frame(height: 160)
    }
}
#endif
```

## designkit.mac.management-list-style

Source: `apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/ManagementListStyleExample.swift`

# EManagementListStyle

ID: designkit.mac.management-list-style
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose

Shared density and control styles for management lists.

## Capabilities
- Plain list — plain list style with the scroll background hidden.
- Compact controls — small switches and borderless buttons inside rows.
- Modifier — applied with .modifier(EManagementListStyle()) on a List.

# EManagementListStyle

ID: designkit.mac.management-list-style
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

管理列表统一使用相同密度与控件样式。

## 能力
- 简洁列表 — plain 列表样式并隐藏滚动背景。
- 紧凑控件 — 行内使用小尺寸开关和无边框按钮。
- 修饰符 — 在 List 上用 .modifier(EManagementListStyle()) 应用。

```swift
#if os(macOS)
import SwiftUI
import DesignKitMac

struct ManagementListStyleExample: View {
    var body: some View {
        List { ESettingsRow("Application") { ESwitch("Enabled", isOn: .constant(true)) } }
            .modifier(EManagementListStyle()).frame(height: 140)
    }
}
#endif
```
