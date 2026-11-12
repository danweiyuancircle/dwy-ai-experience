#if os(macOS)
import SwiftUI
import AppKit

/// 外部进度先通过此边界校验；无效数值由业务转成错误，UI 不截断或伪造百分比。
public struct EProgressFraction: Equatable, Sendable {
    public let value: Double
    public init?(_ value: Double) {
        guard value.isFinite, (0...1).contains(value) else { return nil }
        self.value = value
    }
}

/// 外部任务进度；取消只请求业务取消，不代表任务已经结束。
public struct ETaskProgress<Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let fraction: EProgressFraction?
    private let actions: Actions

    /// fraction=nil 表示不定进度；取消或其他动作在 actions 中明确提供。
    public init(_ title: LocalizedStringResource, fraction: EProgressFraction? = nil,
                @ViewBuilder actions: () -> Actions) {
        self.init(Text(title), fraction: fraction, actions: actions)
    }

    public init(_ title: Text, fraction: EProgressFraction? = nil, @ViewBuilder actions: () -> Actions) {
        self.title = title
        self.fraction = fraction
        self.actions = actions()
    }

    public var body: some View {
        HStack(spacing: theme.spacing.group) {
            if let fraction {
                ProgressView(value: fraction.value) { title }
            } else {
                ProgressView { title }
            }
            actions
        }
    }
}

extension ETaskProgress where Actions == EmptyView {
    public init(_ title: LocalizedStringResource, fraction: EProgressFraction? = nil) {
        self.init(title, fraction: fraction) { EmptyView() }
    }
}

/// 持久非模态通知。错误与需要操作的信息不自动消失，动作不禁用无关区域。
public struct ENotice<Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let tone: EStatusTone
    private let actions: Actions

    public init(_ title: LocalizedStringResource, tone: EStatusTone = .neutral,
                @ViewBuilder actions: () -> Actions) {
        self.init(Text(title), tone: tone, actions: actions)
    }

    public init(_ title: Text, tone: EStatusTone = .neutral, @ViewBuilder actions: () -> Actions) {
        self.title = title
        self.tone = tone
        self.actions = actions()
    }

    public var body: some View {
        ECard {
            VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
                Label { title.fixedSize(horizontal: false, vertical: true) } icon: {
                    Image(systemName: tone.symbol).foregroundStyle(tone.color(theme.colors)).accessibilityHidden(true)
                }
                actions
            }
            .accessibilityElement(children: .contain)
        }
    }
}

extension ENotice where Actions == EmptyView {
    public init(_ title: LocalizedStringResource, tone: EStatusTone = .neutral) {
        self.init(title, tone: tone) { EmptyView() }
    }
}

/// 提示内容明确区分资源和原文；原文即使恰好等于翻译 key 也不经过资源解析。
public enum EToastTitle: Equatable {
    case localized(LocalizedStringResource)
    case verbatim(String)

    func text(locale: Locale) -> Text {
        switch self {
        case .localized(var resource):
            resource.locale = locale
            return Text(resource)
        case .verbatim(let value): return Text(verbatim: value)
        }
    }

    func resolve(locale: Locale) -> String {
        switch self {
        case .localized(var resource):
            resource.locale = locale
            return String(localized: resource)
        case .verbatim(let value): return value
        }
    }
}

/// 简短非关键提示；同文案再次通知使用新 id。需要持续阅读或操作的失败应使用 ENotice。
public struct EToastMessage: Identifiable, Equatable {
    public let id: UUID
    public let title: EToastTitle
    public let tone: EStatusTone

    /// 资源在渲染和公告时使用宿主 locale，保留消费方 bundle。
    public init(_ title: LocalizedStringResource, tone: EStatusTone = .success, id: UUID = UUID()) {
        self.id = id
        self.title = .localized(title)
        self.tone = tone
    }

    /// 已解析文案、用户原文或外部短消息不再作为本地化 key。
    public init(verbatim title: String, tone: EStatusTone = .success, id: UUID = UUID()) {
        self.id = id
        self.title = .verbatim(title)
        self.tone = tone
    }

    func announcement(locale: Locale) -> String { title.resolve(locale: locale) }
}

struct EToastLifetime: Equatable {
    let id: UUID?
    let hovering: Bool
    let focused: Bool
    let voiceOver: Bool

    var expiresAutomatically: Bool { id != nil && !hovering && !focused && !voiceOver }
}

/// 非模态轻提示。悬停、VoiceOver、键盘或可访问焦点期间保留；重要错误请用 ENotice。
public struct EToast: View {
    @Binding private var message: EToastMessage?
    @State private var hovering = false
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOverEnabled
    @Environment(\.locale) private var locale
    private let dismissTitle: Text
    @AccessibilityFocusState private var accessibilityFocused: Bool
    @FocusState private var keyboardFocused: Bool

    public init(message: Binding<EToastMessage?>, dismissTitle: LocalizedStringResource) {
        self.init(message: message, dismissTitle: Text(dismissTitle))
    }

    /// 已解析关闭文案可显式使用 Text(verbatim:)，不丢失原文语义。
    public init(message: Binding<EToastMessage?>, dismissTitle: Text) {
        self._message = message
        self.dismissTitle = dismissTitle
    }

    public var body: some View {
        Group {
            if let message {
                ENotice(message.title.text(locale: locale), tone: message.tone) {
                    EButton(action: { self.message = nil }) { dismissTitle }.focused($keyboardFocused)
                }
                    .accessibilityFocused($accessibilityFocused)
                    .onHover { hovering = $0 }
            }
        }
        .task(id: EToastLifetime(id: message?.id, hovering: hovering, focused: accessibilityFocused || keyboardFocused, voiceOver: voiceOverEnabled)) {
            guard let current = message, !hovering, !accessibilityFocused, !keyboardFocused else { return }
            if voiceOverEnabled {
                NSAccessibility.post(element: NSApp as Any, notification: .announcementRequested,
                                     userInfo: [.announcement: current.announcement(locale: locale),
                                                .priority: NSAccessibilityPriorityLevel.medium.rawValue])
                return
            }
            let lifetime = EToastLifetime(id: current.id, hovering: hovering, focused: accessibilityFocused || keyboardFocused,
                                            voiceOver: voiceOverEnabled)
            guard lifetime.expiresAutomatically else { return }
            do {
                try await Task.sleep(for: .seconds(2))
            } catch {
                // Task.sleep 的取消表示消息替换或宿主退出，不应清掉新消息。
                return
            }
            guard !Task.isCancelled, message?.id == current.id,
                  !hovering, !accessibilityFocused, !keyboardFocused, !voiceOverEnabled else { return }
            message = nil
        }
    }

}
#endif
