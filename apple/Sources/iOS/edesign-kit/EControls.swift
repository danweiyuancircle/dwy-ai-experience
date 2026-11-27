#if os(iOS)
import SwiftUI

/// 操作的重要性与危险角色分开，危险操作仍传原生 ButtonRole。
public enum EButtonEmphasis: Sendable {
    case primary
    case secondary
    case tertiary
}

/// 原生按钮；busy 仅显示外部状态、禁止重复触发，不执行或吞掉业务任务。
public struct EButton<Label: View>: View {
    @Environment(\.eActionGroupExpandsButtons) private var expands
    @Environment(\.eControlTheme) private var theme
    @Environment(\.eControlPlacement) private var placement
    @Environment(\.colorScheme) private var scheme
    @Environment(\.colorSchemeContrast) private var contrast
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    private let emphasis: EButtonEmphasis
    private let role: ButtonRole?
    private let isBusy: Bool
    private let action: () -> Void
    private let label: Label

    public init(
        emphasis: EButtonEmphasis = .secondary,
        role: ButtonRole? = nil,
        isBusy: Bool = false,
        action: @escaping () -> Void,
        @ViewBuilder label: () -> Label
    ) {
        self.emphasis = emphasis
        self.role = role
        self.isBusy = isBusy
        self.action = action
        self.label = label()
    }

    public var body: some View {
        styledButton.disabled(isBusy)
    }

    private var button: some View {
        Button(role: role, action: action) {
            HStack(spacing: theme.spacing.controlGroup) {
                if isBusy { ProgressView().accessibilityHidden(true) }
                label
            }
            .frame(maxWidth: expands ? .infinity : nil)
            .frame(minHeight: theme.size.action)
        }
    }

    @ViewBuilder private var styledButton: some View {
        if #available(iOS 26, *), placement == .floating, !reduceTransparency {
            if emphasis == .primary {
                button.buttonStyle(.glassProminent).tint(tint)
            } else {
                button.buttonStyle(.glass).tint(tint)
            }
        } else {
            switch emphasis {
            case .primary:
                if role == .destructive {
                    button.buttonStyle(.borderedProminent).tint(theme.colors.danger)
                } else {
                    button.buttonStyle(.borderedProminent)
                        .tint(tint)
                        .foregroundStyle(theme.accentPair(scheme: scheme, contrast: contrast).foreground)
                }
            case .secondary:
                button.buttonStyle(.bordered).tint(tint)
            case .tertiary:
                button.buttonStyle(.borderless).tint(tint)
            }
        }
    }

    private var tint: Color {
        role == .destructive ? theme.colors.danger : theme.accentPair(scheme: scheme, contrast: contrast).accent
    }
}

public extension EButton where Label == Text {
    /// 资源由调用方创建，可显式携带其应用/模块 bundle。
    init(
        _ title: LocalizedStringResource,
        emphasis: EButtonEmphasis = .secondary,
        role: ButtonRole? = nil,
        isBusy: Bool = false,
        action: @escaping () -> Void
    ) {
        self.init(emphasis: emphasis, role: role, isBusy: isBusy, action: action) { Text(title) }
    }
}

/// 纯图标操作必须提供可访问名称；图片槽支持 SF Symbol 或调用方资源。
public struct EIconAction<Icon: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let emphasis: EButtonEmphasis
    private let role: ButtonRole?
    private let isBusy: Bool
    private let action: () -> Void
    private let icon: Icon

    public init(
        accessibilityLabel: Text,
        emphasis: EButtonEmphasis = .tertiary,
        role: ButtonRole? = nil,
        isBusy: Bool = false,
        action: @escaping () -> Void,
        @ViewBuilder icon: () -> Icon
    ) {
        title = accessibilityLabel
        self.emphasis = emphasis
        self.role = role
        self.isBusy = isBusy
        self.action = action
        self.icon = icon()
    }

    public var body: some View {
        EButton(emphasis: emphasis, role: role, isBusy: isBusy, action: action) {
            icon.font(.system(size: theme.size.iconGlyph))
                .frame(minWidth: theme.size.iconHit, minHeight: theme.size.iconHit)
        }
        .accessibilityLabel(title)
    }
}

/// 动作菜单保留原生菜单项角色、分组和禁用语义；label 内不要嵌套 Button。
public struct EMenu<Label: View, Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let label: Label
    private let content: Content

    public init(@ViewBuilder content: () -> Content, @ViewBuilder label: () -> Label) {
        self.content = content()
        self.label = label()
    }

    public var body: some View {
        Menu { content } label: { label.frame(minHeight: theme.size.action) }
            .buttonStyle(.bordered)
    }
}

/// 单选呈现独立于动作菜单。调用方为每个选项提供稳定且类型匹配的 tag。
public enum EPickerPresentation: Sendable {
    case menu
    case segmented
}

/// 不因候选增删替调用方改选值；Optional 选择须提供 nil tag 或明确未匹配说明。
public struct EPicker<Selection: Hashable, Label: View, Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Binding private var selection: Selection
    private let presentation: EPickerPresentation
    private let label: Label
    private let content: Content

    public init(
        selection: Binding<Selection>,
        presentation: EPickerPresentation = .menu,
        @ViewBuilder content: () -> Content,
        @ViewBuilder label: () -> Label
    ) {
        _selection = selection
        self.presentation = presentation
        self.content = content()
        self.label = label()
    }

    public var body: some View {
        Group {
            switch presentation {
            case .menu: picker.pickerStyle(.menu)
            case .segmented: picker.pickerStyle(.segmented)
            }
        }
        .frame(minHeight: theme.size.action)
    }

    private var picker: some View { Picker(selection: $selection) { content } label: { label } }
}

/// iOS 原生 switch；状态回写只表达用户选择，后台提交由调用方管理。
public struct ESwitch<Label: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    @Environment(\.colorSchemeContrast) private var contrast
    @Binding private var isOn: Bool
    private let label: Label

    public init(isOn: Binding<Bool>, @ViewBuilder label: () -> Label) {
        _isOn = isOn
        self.label = label()
    }

    public var body: some View {
        Toggle(isOn: $isOn) { label }
            .toggleStyle(.switch)
            .tint(theme.accentPair(scheme: scheme, contrast: contrast).accent)
            .frame(minHeight: theme.size.row)
    }
}

#endif
