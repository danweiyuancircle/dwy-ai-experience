#if os(iOS)
import SwiftUI
import UIKit

/// 单次非模态消息；重复展示也应创建新实例，方便宿主识别消息世代。
public struct ENotice: Identifiable {
    public let id = UUID()
    public let tone: EStatusTone
    private enum Message {
        case localized(LocalizedStringResource)
        case verbatim(String)
    }
    private let message: Message
    let isTransientSuccess: Bool

    /// 重要错误与需阅读消息保持到主动关闭；本地化资源保留调用方 bundle。
    public init(_ message: LocalizedStringResource, tone: EStatusTone = .neutral) {
        self.message = .localized(message)
        self.tone = tone
        isTransientSuccess = false
    }

    /// 用户原文/已解析文本不再作为本地化 key 查找。
    public init(verbatim message: String, tone: EStatusTone = .neutral) {
        self.message = .verbatim(message)
        self.tone = tone
        isTransientSuccess = false
    }

    private init(success message: LocalizedStringResource) {
        self.message = .localized(message)
        tone = .success
        isTransientSuccess = true
    }

    /// 仅非关键成功可自动消失；VoiceOver 开启时仍持续展示供用户阅读。
    public static func transientSuccess(_ message: LocalizedStringResource) -> Self { Self(success: message) }

    var text: Text {
        switch message {
        case .localized(let resource): Text(resource)
        case .verbatim(let original): Text(verbatim: original)
        }
    }

    func announcement(locale: Locale) -> String {
        switch message {
        case .localized(var resource):
            resource.locale = locale
            return String(localized: resource)
        case .verbatim(let original): return original
        }
    }
}

/// 每个展示宿主独立持有；仅管理提示，不阻止页面操作，不持有任何业务任务。
/// 宿主消失时调用 cancelPendingDismissal；重新出现会依据当前消息恢复计时。
@MainActor
@Observable
public final class ENoticeCenter {
    public private(set) var notice: ENotice?
    @ObservationIgnored private var dismissTask: Task<Void, Never>?
    private var voiceOverEnabled = false
    private var interactionActive = false
    private let dismissAfter: Duration

    public init() { dismissAfter = .seconds(2) }

    init(dismissAfter: Duration) { self.dismissAfter = dismissAfter }

    deinit { dismissTask?.cancel() }

    /// 替换与重复消息均取消旧计时，旧任务绝不能清掉后续消息。
    public func show(_ notice: ENotice) {
        self.notice = notice
        scheduleDismissal()
    }

    public func dismiss() {
        cancelPendingDismissal()
        notice = nil
    }

    /// 取消延后更新，保留消息供宿主重新显示；不取消调用方的任务。
    public func cancelPendingDismissal() {
        dismissTask?.cancel()
        dismissTask = nil
    }

    func updateAccessibility(voiceOverEnabled: Bool) {
        self.voiceOverEnabled = voiceOverEnabled
        scheduleDismissal()
    }

    func updateInteraction(active: Bool) {
        interactionActive = active
        scheduleDismissal()
    }

    private func scheduleDismissal() {
        cancelPendingDismissal()
        guard let notice, notice.isTransientSuccess, !voiceOverEnabled, !interactionActive else { return }
        let id = notice.id
        let delay = dismissAfter
        dismissTask = Task { [weak self] in
            do {
                try await Task.sleep(for: delay)
            } catch is CancellationError {
                return
            } catch {
                assertionFailure("Unexpected notice clock error: \(error)")
                return
            }
            guard !Task.isCancelled, let self, self.notice?.id == id else { return }
            self.dismiss()
        }
    }
}

/// 显式挂载的非模态提示宿主，建议放 safeAreaInset。一个 center 对应一个宿主。
/// 关闭名称由产品本地化提供；VoiceOver 开启时自动公告且不定时移除消息。
public struct ENoticeHost: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOverEnabled
    @Environment(\.locale) private var locale
    @AccessibilityFocusState private var accessibilityFocused: Bool
    @FocusState private var keyboardFocused: Bool
    @GestureState private var touchActive = false
    private let center: ENoticeCenter
    private let dismissLabel: Text

    public init(center: ENoticeCenter, dismissLabel: Text) {
        self.center = center
        self.dismissLabel = dismissLabel
    }

    public var body: some View {
        Group {
            if let notice = center.notice {
                EInlineNotice(tone: notice.tone) { notice.text } actions: {
                    EIconAction(accessibilityLabel: dismissLabel, action: center.dismiss) {
                        Image(systemName: "xmark")
                    }
                    .accessibilityFocused($accessibilityFocused)
                    .focused($keyboardFocused)
                }
                .simultaneousGesture(DragGesture(minimumDistance: 0).updating($touchActive) { _, active, _ in
                    active = true
                })
            }
        }
        .onChange(of: voiceOverEnabled, initial: true) { _, enabled in
            center.updateAccessibility(voiceOverEnabled: enabled)
        }
        .onChange(of: center.notice?.id, initial: true) { _, _ in
            if voiceOverEnabled, let notice = center.notice {
                UIAccessibility.post(notification: .announcement, argument: notice.announcement(locale: locale))
            }
        }
        .onChange(of: accessibilityFocused || keyboardFocused || touchActive, initial: true) { _, active in
            center.updateInteraction(active: active)
        }
        .onDisappear { center.cancelPendingDismissal() }
    }
}

/// 持久内联提示，允许明确操作；没有自动计时或模态蒙层。
public struct EInlineNotice<Message: View, Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let tone: EStatusTone
    private let message: Message
    private let actions: Actions

    public init(tone: EStatusTone = .neutral, @ViewBuilder message: () -> Message, @ViewBuilder actions: () -> Actions) {
        self.tone = tone
        self.message = message()
        self.actions = actions()
    }

    public var body: some View {
        ECard {
            VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
                Label { message } icon: { Image(systemName: tone.symbolName) }
                    .foregroundStyle(tone.color(in: theme))
                actions
            }
        }
    }
}

/// 定量进度的外部边界校验；拒绝 NaN/无穷大/越界，不伪造百分比。
public struct EProgressValue: Equatable, Sendable {
    public let fraction: Double

    public enum ValidationError: Error, Equatable { case invalidFraction }

    public init(fraction: Double) throws {
        guard fraction.isFinite, (0...1).contains(fraction) else { throw ValidationError.invalidFraction }
        self.fraction = fraction
    }
}

/// 真实任务阶段由业务回写；取消请求不等于取消完成。
public enum ETaskPhase: Sendable {
    case running
    case cancelling
    case cancelled
    case succeeded
    case failed
}

/// 原生进度与可取消任务展示。nil 表示不定量，不启动任务、不超时、不隐式重试。
public struct ETaskProgress<CancelLabel: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let phase: ETaskPhase
    private let progress: EProgressValue?
    private let cancel: (() -> Void)?
    private let cancelLabel: CancelLabel

    public init(
        title: Text,
        phase: ETaskPhase,
        progress: EProgressValue? = nil,
        cancel: (() -> Void)?,
        @ViewBuilder cancelLabel: () -> CancelLabel
    ) {
        self.title = title
        self.phase = phase
        self.progress = progress
        self.cancel = cancel
        self.cancelLabel = cancelLabel()
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
            title.font(theme.typography.body)
            if phase == .running || phase == .cancelling {
                if let progress { ProgressView(value: progress.fraction).accessibilityLabel(title) }
                else { ProgressView().accessibilityLabel(title) }
            }
            if let cancel, phase == .running {
                EButton(action: cancel) { cancelLabel }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

public extension ETaskProgress where CancelLabel == EmptyView {
    init(title: Text, phase: ETaskPhase, progress: EProgressValue? = nil) {
        self.init(title: title, phase: phase, progress: progress, cancel: nil) { EmptyView() }
    }
}

#endif
