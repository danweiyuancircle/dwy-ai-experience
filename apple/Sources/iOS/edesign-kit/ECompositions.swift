#if os(iOS)
import SwiftUI

/// 内容卡只用不透明动态底色与分隔，不把正文玻璃化。
public struct ECard<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.displayScale) private var displayScale
    private let content: Content

    public init(@ViewBuilder content: () -> Content) { self.content = content() }

    public var body: some View {
        content
            .padding(theme.spacing.cardInset)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(theme.colors.surface, in: RoundedRectangle(cornerRadius: theme.radius.card))
            .overlay {
                RoundedRectangle(cornerRadius: theme.radius.card)
                    .strokeBorder(theme.colors.separator, lineWidth: theme.hairline(displayScale: displayScale))
            }
    }
}

/// 通用设置行；辅助字号时纵排，避免长标签挤掉控件。不附加导航或点击手势。
public struct ESettingsRow<Label: View, Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    private let label: Label
    private let detail: Text?
    private let content: Content

    public init(detail: Text? = nil, @ViewBuilder label: () -> Label, @ViewBuilder content: () -> Content) {
        self.detail = detail
        self.label = label()
        self.content = content()
    }

    public var body: some View {
        if dynamicTypeSize.isAccessibilitySize {
            VStack(alignment: .leading, spacing: theme.spacing.controlGroup) { heading; content }
                .frame(maxWidth: .infinity, minHeight: theme.size.row, alignment: .leading)
        } else {
            HStack(spacing: theme.spacing.formRow) { heading; Spacer(minLength: theme.spacing.controlGroup); content }
                .frame(minHeight: theme.size.row)
        }
    }

    private var heading: some View {
        VStack(alignment: .leading, spacing: theme.spacing.inline) {
            label.font(theme.typography.body)
            if let detail { detail.font(theme.typography.secondary).foregroundStyle(.secondary) }
        }
    }
}

/// 只读标签值；原文通过 Text(verbatim:) 提供，保留换行和选择能力。
public struct ELabelValue<Label: View, Value: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let label: Label
    private let value: Value

    public init(@ViewBuilder label: () -> Label, @ViewBuilder value: () -> Value) {
        self.label = label()
        self.value = value()
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.fieldLabel) {
            label.font(theme.typography.caption).foregroundStyle(.secondary)
            value.font(theme.typography.body).textSelection(.enabled)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// 状态语义与品牌色独立，图标和文字同时表达状态。
public enum EStatusTone: String, CaseIterable, Sendable {
    case neutral
    case success
    case warning
    case error

    public var symbolName: String {
        switch self {
        case .neutral: "info.circle"
        case .success: "checkmark.circle"
        case .warning: "exclamationmark.triangle"
        case .error: "exclamationmark.circle"
        }
    }

    func color(in theme: EControlTheme) -> Color {
        switch self {
        case .neutral: theme.colors.primary
        case .success: theme.colors.success
        case .warning: theme.colors.warning
        case .error: theme.colors.danger
        }
    }
}

/// 非交互状态标签不隐含按钮；长状态文案可换行。
public struct EStatusBadge: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let tone: EStatusTone

    public init(_ title: Text, tone: EStatusTone = .neutral) {
        self.title = title
        self.tone = tone
    }

    public var body: some View {
        Label { title } icon: { Image(systemName: tone.symbolName) }
            .font(theme.typography.caption)
            .foregroundStyle(tone.color(in: theme))
            .padding(theme.spacing.controlGroup)
            .background(theme.colors.selection, in: Capsule())
    }
}

/// 内容结果必须由业务明确提供，不能根据空集合推断加载或成功。
public enum EContentState: Hashable, Sendable {
    case idle
    case loading
    case success
    case empty
    case failure
}

/// 空/错误/加载等通用占位；后续动作完全由调用方提供，不自动重试。
public struct EStateView<Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let state: EContentState
    private let title: Text
    private let detail: Text?
    private let actions: Actions

    public init(
        state: EContentState,
        title: Text,
        detail: Text? = nil,
        @ViewBuilder actions: () -> Actions
    ) {
        self.state = state
        self.title = title
        self.detail = detail
        self.actions = actions()
    }

    public var body: some View {
        VStack(spacing: theme.spacing.group) {
            if state == .loading {
                ProgressView().accessibilityHidden(true)
            } else {
                Image(systemName: symbol).font(.title).foregroundStyle(.secondary).accessibilityHidden(true)
            }
            title.font(theme.typography.sectionTitle)
            if let detail { detail.font(theme.typography.secondary).foregroundStyle(.secondary) }
            actions
        }
        .multilineTextAlignment(.center)
        .frame(maxWidth: .infinity)
        .padding(theme.spacing.section)
    }

    private var symbol: String {
        switch state {
        case .idle: "circle.dashed"
        case .loading: "hourglass"
        case .success: "checkmark.circle"
        case .empty: "tray"
        case .failure: "exclamationmark.triangle"
        }
    }
}

public extension EStateView where Actions == EmptyView {
    init(state: EContentState, title: Text, detail: Text? = nil) {
        self.init(state: state, title: title, detail: detail) { EmptyView() }
    }
}

#endif
