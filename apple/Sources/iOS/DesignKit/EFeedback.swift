#if os(iOS)
import SwiftUI
import UIKit
import DesignCore

/// 单次非模态消息；重复展示也应创建新实例，方便宿主识别消息世代。
public struct ENotice: Identifiable {
    public let id = UUID()
    public let tone: EStatusTone
    /// 默认跟随状态语义；仅日志等明确操作反馈使用自己的 SF Symbol。
    public let systemImage: String
    private enum Message {
        case localized(LocalizedStringResource)
        case verbatim(String)
    }
    private let message: Message
    let isTransient: Bool

    /// 重要错误与需阅读消息保持到主动关闭；本地化资源保留调用方 bundle。
    public init(_ message: LocalizedStringResource, tone: EStatusTone = .neutral) {
        self.message = .localized(message)
        self.tone = tone
        systemImage = tone.symbolName
        isTransient = false
    }

    /// 用户原文/已解析文本不再作为本地化 key 查找。
    public init(verbatim message: String, tone: EStatusTone = .neutral) {
        self.message = .verbatim(message)
        self.tone = tone
        systemImage = tone.symbolName
        isTransient = false
    }

    private init(success message: LocalizedStringResource) {
        self.message = .localized(message)
        tone = .success
        systemImage = EStatusTone.success.symbolName
        isTransient = true
    }

    /// 仅非关键成功可自动消失；VoiceOver 开启时仍持续展示供用户阅读。
    public static func transientSuccess(_ message: LocalizedStringResource) -> Self { Self(success: message) }

    private init(transient message: String, tone: EStatusTone, systemImage: String) {
        self.message = .verbatim(message)
        self.tone = tone
        self.systemImage = systemImage
        isTransient = true
    }

    /// 已解析的短反馈不再查本地化；需阅读或操作的错误必须使用持久消息初始化器。
    public static func transient(verbatim message: String, tone: EStatusTone = .success,
                                 systemImage: String? = nil) -> Self {
        Self(transient: message, tone: tone, systemImage: systemImage ?? tone.symbolName)
    }

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

    /// 消费方可沿用既有短反馈时长；读屏或交互期间仍暂停计时。
    public init(dismissAfter: Duration) { self.dismissAfter = dismissAfter }

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
        guard let notice, notice.isTransient, !voiceOverEnabled, !interactionActive else { return }
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
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOverEnabled
    @Environment(\.locale) private var locale
    @AccessibilityFocusState private var accessibilityFocused: Bool
    @FocusState private var keyboardFocused: Bool
    @GestureState private var touchActive = false
    private let center: ENoticeCenter
    private let dismissLabel: Text
    private let actions: AnyView

    /// actions 仅用于持久通知；业务自行决定操作后关闭还是更新消息。
    public init<Actions: View>(center: ENoticeCenter, dismissLabel: Text, @ViewBuilder actions: () -> Actions) {
        self.center = center
        self.dismissLabel = dismissLabel
        self.actions = AnyView(actions())
    }

    public init(center: ENoticeCenter, dismissLabel: Text) {
        self.init(center: center, dismissLabel: dismissLabel) { EmptyView() }
    }

    public var body: some View {
        Group {
            if let notice = center.notice {
                if notice.isTransient {
                    EToast(notice.text, tone: notice.tone, systemImage: notice.systemImage)
                        .accessibilityIdentifier("notice.toast")
                        .accessibilityAction(named: dismissLabel, center.dismiss)
                        .accessibilityFocused($accessibilityFocused)
                        .allowsHitTesting(voiceOverEnabled)
                        .transition(.opacity)
                } else {
                    EInlineNotice(tone: notice.tone) { notice.text } actions: {
                        HStack(spacing: 0) {
                            actions
                            EIconAction(accessibilityLabel: dismissLabel, action: center.dismiss) {
                                Image(systemName: "xmark")
                                    .font(theme.typography.secondary)
                                    .foregroundStyle(theme.colors.secondary)
                            }
                            .accessibilityFocused($accessibilityFocused)
                            .focused($keyboardFocused)
                        }
                    }
                    .simultaneousGesture(DragGesture(minimumDistance: 0).updating($touchActive) { _, active, _ in
                        active = true
                    })
                    .transition(.opacity)
                }
            }
        }
        .animation(reduceMotion ? nil : Motion.soft, value: center.notice?.id)
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

/// 只绘制紧凑短反馈；呈现位置与计时由 ENoticeHost 和 ENoticeCenter 管理。
public struct EToast: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.displayScale) private var displayScale
    private let message: Text
    private let tone: EStatusTone
    private let systemImage: String

    public init(_ message: Text, tone: EStatusTone = .success, systemImage: String? = nil) {
        self.message = message
        self.tone = tone
        self.systemImage = systemImage ?? tone.symbolName
    }

    public var body: some View {
        HStack(spacing: theme.spacing.controlGroup) {
            Image(systemName: systemImage)
                .foregroundStyle(tone.color(in: theme)).accessibilityHidden(true)
            message.foregroundStyle(theme.colors.primary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .font(theme.typography.secondary)
        .padding(.horizontal, theme.spacing.group)
        .padding(.vertical, 10)
        .background(theme.colors.surface, in: RoundedRectangle(cornerRadius: theme.radius.card))
        .overlay {
            RoundedRectangle(cornerRadius: theme.radius.card)
                .strokeBorder(theme.colors.separator, lineWidth: theme.hairline(displayScale: displayScale))
        }
        .accessibilityElement(children: .combine)
    }
}

/// 持久内联提示，允许明确操作；没有自动计时或模态蒙层。
public struct EInlineNotice<Message: View, Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.displayScale) private var displayScale
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    private let tone: EStatusTone
    private let message: Message
    private let actions: Actions

    public init(tone: EStatusTone = .neutral, @ViewBuilder message: () -> Message, @ViewBuilder actions: () -> Actions) {
        self.tone = tone
        self.message = message()
        self.actions = actions()
    }

    public var body: some View {
        Group {
            if dynamicTypeSize.isAccessibilitySize {
                expanded
            } else {
                ViewThatFits(in: .horizontal) {
                    HStack(spacing: theme.spacing.controlGroup) {
                        label
                        Spacer(minLength: 0)
                        actions.fixedSize(horizontal: true, vertical: false)
                    }
                    expanded
                }
            }
        }
        .font(theme.typography.secondary)
        .frame(minHeight: theme.size.iconHit)
        .padding(.leading, theme.spacing.group)
        .padding(.trailing, theme.spacing.inline)
        .padding(.vertical, theme.spacing.inline)
        .background(theme.colors.surface, in: RoundedRectangle(cornerRadius: theme.radius.card))
        .overlay {
            RoundedRectangle(cornerRadius: theme.radius.card)
                .strokeBorder(theme.colors.separator, lineWidth: theme.hairline(displayScale: displayScale))
        }
    }

    private var label: some View {
        Label {
            message.foregroundStyle(theme.colors.primary).fixedSize(horizontal: false, vertical: true)
        } icon: {
            Image(systemName: tone.symbolName).foregroundStyle(tone.color(in: theme)).accessibilityHidden(true)
        }
    }

    private var expanded: some View {
        VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
            label
            actions.frame(maxWidth: .infinity, alignment: .trailing)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
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
