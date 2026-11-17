import SwiftUI
#if os(iOS)
import DesignKitIOS
#elseif os(macOS)
import DesignKitMac
#endif

/// 拒绝后的说明组合；文案、设置跳转和业务恢复均由宿主提供，不自动索取权限。
public struct PermissionExplanation: View {
    private let title: String
    private let message: String
    private let settingsTitle: String
    private let retryTitle: String
    private let openSettings: @MainActor () async -> Void
    private let retry: @MainActor () async -> Void
    private enum Action: Equatable, Sendable { case settings, retry }
    @State private var action: Action?

    /// openSettings 必须处理跳转失败；retry 应先读取系统状态，再决定是否继续业务。
    public init(title: String, message: String, settingsTitle: String, retryTitle: String,
                openSettings: @escaping @MainActor () async -> Void,
                retry: @escaping @MainActor () async -> Void) {
        self.title = title
        self.message = message
        self.settingsTitle = settingsTitle
        self.retryTitle = retryTitle
        self.openSettings = openSettings
        self.retry = retry
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(verbatim: title).font(.headline).accessibilityAddTraits(.isHeader)
            Text(verbatim: message).fixedSize(horizontal: false, vertical: true)
            EButton {
                action = .settings
            } label: { Text(verbatim: settingsTitle) }
            EButton {
                action = .retry
            } label: { Text(verbatim: retryTitle) }
        }
        .disabled(action != nil)
        .task(id: action) {
            guard let action else { return }
            // 旧页面的取消任务结束时，不能清掉重新进入页面后触发的新动作。
            defer { if !Task.isCancelled { self.action = nil } }
            switch action {
            case .settings: await openSettings()
            case .retry: await retry()
            }
        }
        .onDisappear { action = nil }
    }
}
