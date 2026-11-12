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

/// 简短非关键成功信息；相同文字的再次通知也使用新的 id，重新计算展示时长。
public struct EToastMessage: Identifiable, Equatable {
    public let id: UUID
    public let title: LocalizedStringResource

    public init(_ title: LocalizedStringResource, id: UUID = UUID()) {
        self.id = id
        self.title = title
    }

    func announcement(locale: Locale) -> String {
        var resource = title
        resource.locale = locale
        return String(localized: resource)
    }
}

struct EToastLifetime: Equatable {
    let id: UUID?
    let hovering: Bool
    let focused: Bool
    let voiceOver: Bool

    var expiresAutomatically: Bool { id != nil && !hovering && !focused && !voiceOver }
}

/// 非模态成功提示。悬停、VoiceOver 或可访问焦点期间保留；重要错误请用 ENotice。
public struct EToast: View {
    @Binding private var message: EToastMessage?
    @State private var hovering = false
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOverEnabled
    @Environment(\.locale) private var locale
    private let dismissTitle: LocalizedStringResource
    @AccessibilityFocusState private var accessibilityFocused: Bool
    @FocusState private var keyboardFocused: Bool

    public init(message: Binding<EToastMessage?>, dismissTitle: LocalizedStringResource) {
        self._message = message
        self.dismissTitle = dismissTitle
    }

    public var body: some View {
        Group {
            if let message {
                ENotice(message.title, tone: .success) {
                    EButton(dismissTitle) { self.message = nil }.focused($keyboardFocused)
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
            guard message?.id == current.id else { return }
            message = nil
        }
    }

}
#endif
