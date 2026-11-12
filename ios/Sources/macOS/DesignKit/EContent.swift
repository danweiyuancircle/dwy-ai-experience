#if os(macOS)
import SwiftUI

/// 内容卡使用稳定不透明语义底色；不是玻璃操作层，也不自行决定点击或导航。
public struct ECard<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.displayScale) private var scale
    private let content: Content

    public init(@ViewBuilder content: () -> Content) { self.content = content() }

    public var body: some View {
        content
            .padding(theme.spacing.cardInset)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(theme.colors.surface, in: RoundedRectangle(cornerRadius: theme.cardRadius))
            .overlay {
                RoundedRectangle(cornerRadius: theme.cardRadius)
                    .strokeBorder(theme.colors.separator, lineWidth: 1 / scale)
            }
    }
}

/// 设置行的说明与原生控件槽，宽度不足时纵向排列，不固定整行高度。
public struct ESettingsRow<Control: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let detail: Text?
    private let control: Control

    public init(_ title: LocalizedStringResource, detail: LocalizedStringResource? = nil,
                @ViewBuilder control: () -> Control) {
        self.init(Text(title), detail: detail.map { Text($0) }, control: control)
    }

    public init(_ title: Text, detail: Text? = nil, @ViewBuilder control: () -> Control) {
        self.title = title
        self.detail = detail
        self.control = control()
    }

    private var label: some View {
        VStack(alignment: .leading, spacing: theme.spacing.inline) {
            title.font(theme.typography.body)
            if let detail {
                detail.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    public var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: theme.spacing.group) {
                label
                Spacer(minLength: theme.spacing.group)
                control.accessibilityLabel(title)
            }
            VStack(alignment: .leading, spacing: theme.spacing.formRow) {
                label
                control.accessibilityLabel(title)
            }
        }
        .accessibilityElement(children: .contain)
    }
}

/// 静态标签值，值可使用 Text(verbatim:) 或格式化 Text；不猜测业务数据状态。
public struct ELabelValue: View {
    private let title: Text
    private let value: Text

    public init(_ title: LocalizedStringResource, value: Text) {
        self.title = Text(title)
        self.value = value
    }

    public var body: some View {
        ESettingsRow(title) { value.textSelection(.enabled) }
    }
}

/// 非业务状态的视觉语义，状态仍须配有可读文字。
public enum EStatusTone: Sendable {
    case neutral, success, warning, failure

    func color(_ colors: ESemanticColors) -> Color {
        switch self {
        case .neutral: colors.secondaryText
        case .success: colors.success
        case .warning: colors.warning
        case .failure: colors.danger
        }
    }

    var symbol: String {
        switch self {
        case .neutral: "info.circle"
        case .success: "checkmark.circle"
        case .warning: "exclamationmark.triangle"
        case .failure: "xmark.octagon"
        }
    }
}

/// 状态标签保留文字与图标，不仅用颜色区分结果。
public struct EStatusBadge: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let tone: EStatusTone

    public init(_ title: LocalizedStringResource, tone: EStatusTone = .neutral) {
        self.init(Text(title), tone: tone)
    }

    public init(_ title: Text, tone: EStatusTone = .neutral) {
        self.title = title
        self.tone = tone
    }

    public var body: some View {
        Label { title } icon: { Image(systemName: tone.symbol).accessibilityHidden(true) }
            .font(theme.typography.caption)
            .foregroundStyle(tone.color(theme.colors))
            .padding(theme.spacing.inline)
            .background(theme.colors.surface, in: Capsule())
            .accessibilityElement(children: .combine)
    }
}

/// 内容状态由业务显式指定，不以空数组推断加载或失败。
public enum EContentPhase: Sendable { case idle, loading, empty, failure, success }

/// 首屏加载、空态与错误共用的展示组合；动作由调用方提供，不隐式启动或重试任务。
public struct EContentState<Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let phase: EContentPhase
    private let title: Text
    private let detail: Text?
    private let actions: Actions

    public init(_ phase: EContentPhase, title: LocalizedStringResource,
                detail: LocalizedStringResource? = nil, @ViewBuilder actions: () -> Actions) {
        self.init(phase, title: Text(title), detail: detail.map { Text($0) }, actions: actions)
    }

    public init(_ phase: EContentPhase, title: Text, detail: Text? = nil,
                @ViewBuilder actions: () -> Actions) {
        self.phase = phase
        self.title = title
        self.detail = detail
        self.actions = actions()
    }

    public var body: some View {
        VStack(spacing: theme.spacing.group) {
            if phase == .loading {
                ProgressView().accessibilityHidden(true)
            } else {
                Image(systemName: phase == .failure ? "exclamationmark.triangle" : phase == .success ? "checkmark.circle" : "tray")
                    .foregroundStyle(phase == .failure ? theme.colors.danger : theme.colors.secondaryText)
                    .accessibilityHidden(true)
            }
            title.font(theme.typography.sectionTitle)
            if let detail {
                detail.foregroundStyle(theme.colors.secondaryText).fixedSize(horizontal: false, vertical: true)
            }
            actions
        }
        .multilineTextAlignment(.center)
        .padding(theme.spacing.pageInset)
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .contain)
    }
}

extension EContentState where Actions == EmptyView {
    public init(_ phase: EContentPhase, title: LocalizedStringResource,
                detail: LocalizedStringResource? = nil) {
        self.init(phase, title: title, detail: detail) { EmptyView() }
    }
}
#endif
