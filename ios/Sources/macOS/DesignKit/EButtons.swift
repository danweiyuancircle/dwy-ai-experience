#if os(macOS)
import SwiftUI

/// 操作层级；危险语义单独通过原生 ButtonRole 提供。
public enum EButtonEmphasis: Sendable {
    case primary
    case secondary
    case plain
}

/// 通用 Mac 操作按钮。业务方负责动作和状态；原生 Button 保留键盘、角色及辅助功能行为。
public struct EButton<Label: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let emphasis: EButtonEmphasis
    private let role: ButtonRole?
    private let isBusy: Bool
    private let action: () -> Void
    private let label: Label

    /// 自定义标签可放 SF Symbol、资源图片或进度文案；图标独占时须提供可访问名称。
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

    /// 文字按钮；title 由调用方本地化，组件不绑定应用的本地化单例。
    public init(
        _ title: LocalizedStringResource,
        emphasis: EButtonEmphasis = .secondary,
        role: ButtonRole? = nil,
        isBusy: Bool = false,
        action: @escaping () -> Void
    ) where Label == Text {
        self.init(emphasis: emphasis, role: role, isBusy: isBusy, action: action) { Text(title) }
    }

    public var body: some View {
        Button(role: role, action: action) {
            HStack(spacing: theme.spacing.fieldLabel) {
                if isBusy {
                    ProgressView().controlSize(.small).accessibilityHidden(true)
                }
                label
            }
        }
        .modifier(EButtonChrome(emphasis: emphasis))
        .tint(role == .destructive ? theme.colors.danger : theme.accent)
        .disabled(isBusy)
    }
}

/// 图标操作按钮。title 同时用于 VoiceOver 与 help，图片内容通过 label 提供。
public struct EIconAction<Icon: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.eControlPlacement) private var placement
    private let title: Text
    private let role: ButtonRole?
    private let isBusy: Bool
    private let action: () -> Void
    private let icon: Icon

    /// 用自定义图片作为按钮内容；资源加载由应用负责，不把应用资源名写入公共库。
    public init(
        _ title: LocalizedStringResource,
        role: ButtonRole? = nil,
        isBusy: Bool = false,
        action: @escaping () -> Void,
        @ViewBuilder icon: () -> Icon
    ) {
        self.init(Text(title), role: role, isBusy: isBusy, action: action, icon: icon)
    }

    /// 已本地化或原文名称用 Text 显式传入，不丢失 bundle 与 verbatim 语义。
    public init(
        _ title: Text,
        role: ButtonRole? = nil,
        isBusy: Bool = false,
        action: @escaping () -> Void,
        @ViewBuilder icon: () -> Icon
    ) {
        self.title = title
        self.role = role
        self.isBusy = isBusy
        self.action = action
        self.icon = icon()
    }

    /// 使用系统 SF Symbol；title 必须是有意义的本地化操作名称。
    public init(
        _ title: LocalizedStringResource,
        systemImage: String,
        role: ButtonRole? = nil,
        isBusy: Bool = false,
        action: @escaping () -> Void
    ) where Icon == Image {
        self.init(title, role: role, isBusy: isBusy, action: action) { Image(systemName: systemImage) }
    }

    public var body: some View {
        let side = placement == .content ? theme.iconSide : theme.chromeIconSide
        EButton(role: role, isBusy: isBusy, action: action) {
            icon.frame(minWidth: side, minHeight: side).contentShape(Circle())
        }
        .buttonBorderShape(.circle)
        .accessibilityLabel(title)
        .help(title)
    }
}

struct EButtonChrome: ViewModifier {
    @Environment(\.eControlPlacement) private var placement
    let emphasis: EButtonEmphasis

    @ViewBuilder
    func body(content: Content) -> some View {
        switch (placement, emphasis) {
        case (_, .plain): content.buttonStyle(.borderless)
        case (.floating, .primary): content.buttonStyle(.glassProminent)
        case (.floating, .secondary): content.buttonStyle(.glass)
        case (_, .primary): content.buttonStyle(.borderedProminent)
        case (.toolbar, .secondary): content.buttonStyle(.borderless)
        case (.content, .secondary): content.buttonStyle(.bordered)
        }
    }
}

/// 同一操作区域；浮动场景共享玻璃采样，内容区和工具栏不额外生成玻璃背景。
public struct EActionGroup<Content: View>: View {
    @Environment(\.eControlPlacement) private var placement
    private let spacing: CGFloat
    private let content: Content

    /// spacing 同时控制布局间距与玻璃容器的邻近阈值；不要用此容器包裹整页内容。
    public init(spacing: CGFloat = 8, @ViewBuilder content: () -> Content) {
        self.spacing = spacing
        self.content = content()
    }

    public var body: some View {
        if placement == .floating {
            GlassEffectContainer(spacing: spacing) { HStack(spacing: spacing) { content } }
        } else {
            HStack(spacing: spacing) { content }
        }
    }
}
#endif
