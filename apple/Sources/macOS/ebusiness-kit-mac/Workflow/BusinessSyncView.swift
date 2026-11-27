#if os(macOS)
import DesignKitMac
import SwiftUI
import SyncCore

/// 显示同步进度、待处理数量及最近成功时间，可由宿主显式同步。
public struct BusinessSyncView: View {
    private let coordinator: SyncCoordinator?
    private let suppliedState: SyncState?
    private let onSynchronize: (@MainActor () async throws -> Void)?
    @Environment(\.eControlTheme) private var theme
    @State private var coordinatorState: SyncState?
    @State private var busy = false
    @State private var failed = false

    /// 订阅已有协调器，不启动自动同步。按钮仅调用显式 synchronize。
    public init(coordinator: SyncCoordinator) {
        self.coordinator = coordinator
        self.suppliedState = nil
        self.onSynchronize = { try await coordinator.synchronize() }
    }

    /// 供已有状态流的宿主展示其快照，nil 表示尚无初始状态。
    public init(state: SyncState?, onSynchronize: (@MainActor () async throws -> Void)? = nil) {
        self.coordinator = nil
        self.suppliedState = state
        self.onSynchronize = onSynchronize
    }

    private var state: SyncState? { coordinator == nil ? suppliedState : coordinatorState }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.group) {
            EPageHeader(title: workflowText("sync.title"))
            ECard {
                if let state {
                    content(state)
                } else {
                    EContentState(.loading, title: workflowText("sync.loading")) { EmptyView() }
                }
            }
            if failed { EStatusBadge(workflowText("sync.operationFailed"), tone: .failure) }
        }
        .task(id: coordinator.map(ObjectIdentifier.init)) {
            coordinatorState = nil
            guard let coordinator else { return }
            for await snapshot in await coordinator.states() {
                guard !Task.isCancelled else { return }
                coordinatorState = snapshot
            }
        }
        .onChange(of: state?.lastSuccessfulSync) { _, lastSync in
            if lastSync != nil { failed = false }
        }
    }

    private func content(_ state: SyncState) -> some View {
        let presentation = Self.presentation(for: state.phase)
        return VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
            EStatusBadge(workflowText(presentation.title), tone: presentation.tone)
            ELabelValue(workflowText("sync.pending"), value: Text(state.pendingCount, format: .number))
            ELabelValue(workflowText("sync.conflicts"), value: Text(state.conflictCount, format: .number))
            if let lastSync = state.lastSuccessfulSync {
                ELabelValue(workflowText("sync.lastSuccess"), value: Text(lastSync, format: .dateTime))
            }
            if let onSynchronize {
                EButton(emphasis: .secondary, isBusy: busy, action: { synchronize(onSynchronize) }) {
                    workflowText("sync.now")
                }
                .disabled(busy || !presentation.canSynchronize)
            }
        }
    }

    private func synchronize(_ operation: @escaping @MainActor () async throws -> Void) {
        guard !busy, let state, Self.presentation(for: state.phase).canSynchronize else { return }
        busy = true
        failed = false
        Task {
            defer { busy = false }
            do {
                try await operation()
            } catch is CancellationError {
                return
            } catch {
                failed = true
            }
        }
    }

    static func presentation(for phase: SyncPhase) -> (title: LocalizedStringKey, tone: EStatusTone, canSynchronize: Bool) {
        switch phase {
        case .idle: ("sync.idle", .success, true)
        case .localOnly: ("sync.localOnly", .neutral, false)
        case .syncing: ("sync.syncing", .neutral, false)
        case .waitingForRetry: ("sync.waitingForRetry", .warning, true)
        case .paused: ("sync.paused", .neutral, false)
        case .requiresAuthentication: ("sync.requiresAuthentication", .warning, false)
        case .identityChanged: ("sync.identityChanged", .warning, false)
        case .failed: ("sync.failed", .failure, true)
        }
    }
}
#endif
