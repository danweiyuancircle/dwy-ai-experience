import Foundation

/// 同步阶段独立于网络连接与业务设备连接状态。
public enum SyncPhase: String, Sendable {
    case idle, localOnly, syncing, waitingForRetry, paused, requiresAuthentication, identityChanged, failed
}

/// 对外只提供安全的错误代码；不包含令牌或业务正文。
public struct SyncState: Sendable, Equatable {
    public let phase: SyncPhase
    public let pendingCount: Int
    public let conflictCount: Int
    public let lastSuccessfulSync: Date?
    public let errorCode: String?
}

/// 自动触发时的有限重试策略；显式 synchronize 失败直接交还调用者。
public struct SyncRetryPolicy: Sendable {
    public let maximumAttempts: Int
    public let initialDelay: TimeInterval
    public let maximumDelay: TimeInterval

    public init(maximumAttempts: Int, initialDelay: TimeInterval, maximumDelay: TimeInterval) throws {
        guard (1...10).contains(maximumAttempts), initialDelay.isFinite, maximumDelay.isFinite,
              initialDelay >= 0, maximumDelay >= initialDelay, maximumDelay <= 3600 else {
            throw SyncError.invalidConfiguration("重试次数须为 1...10，延迟须为 0...3600 秒")
        }
        self.maximumAttempts = maximumAttempts
        self.initialDelay = initialDelay
        self.maximumDelay = maximumDelay
    }
}

/// 单一账号作用域的同步执行器。宿主必须在退出或切号前 pause，不能靠 actor 隔离代替世代校验。
public actor SyncCoordinator {
    private let store: SyncStore
    private let transport: any SyncTransport
    private let identityProvider: @Sendable (Bool) async throws -> SyncIdentity
    private let retryPolicy: SyncRetryPolicy
    private let sleep: @Sendable (TimeInterval) async throws -> Void
    private var generation: UInt64 = 0
    private var execution = SyncExecutionLease()
    private var isPaused = false
    private var isRecovering = false
    private var cycleTask: Task<Void, Error>?
    private var automaticTask: Task<Void, Never>?
    private var observationTask: Task<Void, Never>?
    private var requestedAgain = false
    private var observedLocalChangeSequence: Int64 = 0
    private var observers: [UUID: AsyncStream<SyncState>.Continuation] = [:]
    private var state = SyncState(phase: .idle, pendingCount: 0, conflictCount: 0, lastSuccessfulSync: nil, errorCode: nil)

    /// identityProvider(false) 取得可用会话，true 仅在 401 后要求刷新一次；不得返回其他账号身份。
    public init(
        store: SyncStore,
        transport: any SyncTransport,
        identityProvider: @escaping @Sendable (_ forceRefresh: Bool) async throws -> SyncIdentity,
        retryPolicy: SyncRetryPolicy,
        sleep: @escaping @Sendable (TimeInterval) async throws -> Void = { seconds in
            // 避免旧 Swift 泛型时钟异步帧崩溃；超长 Retry-After 饱和为可表示的纳秒上限。
            let nanoseconds = min(seconds * 1_000_000_000, Double(Int64.max).nextDown)
            try await Task.sleep(nanoseconds: UInt64(nanoseconds))
        }
    ) {
        self.store = store
        self.transport = transport
        self.identityProvider = identityProvider
        self.retryPolicy = retryPolicy
        self.sleep = sleep
    }

    /// 显式执行一轮，合并同时到达的调用；网络失败不在此接口内隐式重试。
    public func synchronize() async throws {
        guard !isPaused else { throw CancellationError() }
        if let cycleTask { try await cycleTask.value; return }
        let epoch = generation
        let task = Task { try await self.runCycle(epoch: epoch) }
        cycleTask = task
        defer { if generation == epoch { cycleTask = nil } }
        try await task.value
    }

    /// 开启本地提交观察并触发同步；前台与网络恢复时可重复调用以重新触发。
    public func start() {
        resumeExecution()
        observeLocalChanges()
        requestAutomaticSync()
    }

    /// 开启本地提交观察并等待一轮；失败直接抛出，不额外启动自动轮次。
    public func startAndSynchronize() async throws {
        resumeExecution()
        try await updateCounts(epoch: generation, consumeLocalChanges: true)
        observeLocalChanges()
        try await synchronize()
    }

    private func resumeExecution() {
        if isPaused { execution = SyncExecutionLease() }
        isPaused = false
    }

    private func observeLocalChanges() {
        if observationTask == nil {
            observationTask = Task { [weak self, store] in
                let stream = await store.changes()
                for await snapshot in stream {
                    guard !Task.isCancelled else { break }
                    await self?.localStoreChanged(snapshot)
                }
            }
        }
    }

    /// 必须在宿主卸载账号库前调用；即使网络不响应取消，旧回调也会被世代拒绝。
    public func pause() {
        execution.invalidate()
        isPaused = true
        isRecovering = false
        generation &+= 1
        cycleTask?.cancel()
        automaticTask?.cancel()
        observationTask?.cancel()
        cycleTask = nil
        automaticTask = nil
        observationTask = nil
        requestedAgain = false
        publish(phase: .paused)
    }

    /// 状态流带初始值；消费者结束时移除 continuation，避免常驻页面泄漏。
    public func states() -> AsyncStream<SyncState> {
        let id = UUID()
        return AsyncStream(bufferingPolicy: .bufferingNewest(1)) { continuation in
            observers[id] = continuation
            continuation.yield(state)
            continuation.onTermination = { [weak self] _ in
                Task { await self?.removeObserver(id) }
            }
        }
    }

    /// 恢复新设备身份前先暂停执行器；旧冻结请求必须显式变成待解决冲突，不能自动换 ID 重放。
    public func recoverDeviceIdentity() async throws {
        if isRecovering, let cycleTask { try await cycleTask.value; return }
        pause()
        execution = SyncExecutionLease()
        isPaused = false
        isRecovering = true
        let epoch = generation
        let lease = execution
        let task = Task { try await self.runRecovery(epoch: epoch, execution: lease) }
        cycleTask = task
        defer { if generation == epoch { cycleTask = nil; isRecovering = false } }
        try await task.value
    }

    private func runRecovery(epoch: UInt64, execution: SyncExecutionLease) async throws {
        guard store.scope.userID != nil else { throw SyncError.scopeMismatch }
        guard transport.scope == store.scope else { throw SyncError.scopeMismatch }
        let identity = try await identityProvider(false)
        try check(epoch)
        try validate(identity)
        try await pullAll(identity: identity, epoch: epoch, execution: execution)
        try check(epoch)
        try await store.quarantinePendingOperations(newDeviceID: identity.deviceID, execution: execution)
        try check(epoch)
        try await updateCounts(epoch: epoch)
        publish(phase: .idle)
    }

    private func runCycle(epoch: UInt64) async throws {
        let lease = execution
        do {
            try check(epoch)
            if store.scope.userID == nil {
                try await updateCounts(epoch: epoch)
                publish(phase: .localOnly)
                return
            }
            guard transport.scope == store.scope else { throw SyncError.scopeMismatch }
            try await updateCounts(epoch: epoch, consumeLocalChanges: true)
            publish(phase: .syncing)
            var identity = try await identityProvider(false)
            try check(epoch)
            try validate(identity)
            try await store.bindDevice(identity.deviceID, execution: lease)
            try check(epoch)
            do {
                try await runPass(identity: identity, epoch: epoch, execution: lease)
            } catch let error as SyncServerError where error.statusCode == 401 {
                identity = try await identityProvider(true)
                try check(epoch)
                try validate(identity)
                try await store.bindDevice(identity.deviceID, execution: lease)
                try check(epoch)
                // 已提交部分通过持久化回执对账；不改变任何冻结请求。
                try await runPass(identity: identity, epoch: epoch, execution: lease)
            }
            try check(epoch)
            try await updateCounts(epoch: epoch)
            publish(phase: .idle, success: Date())
        } catch {
            guard epoch == generation, !isPaused, !Task.isCancelled else { throw CancellationError() }
            // 请求期间仍可本地编辑；失败状态不能用旧统计覆盖已持久化的队列计数。
            try await updateCounts(epoch: epoch, consumeLocalChanges: true)
            requestedAgain = false
            if let syncError = error as? SyncError, syncError == .identityChanged {
                publish(phase: .identityChanged, errorCode: "identity_changed")
            } else if let server = error as? SyncServerError {
                publish(phase: server.statusCode == 401 ? .requiresAuthentication : .failed, errorCode: server.code)
            } else {
                publish(phase: .failed, errorCode: error is URLError ? "network_error" : "sync_error")
            }
            throw error
        }
    }

    private func runPass(identity: SyncIdentity, epoch: UInt64, execution: SyncExecutionLease) async throws {
        try await pullAll(identity: identity, epoch: epoch, execution: execution)
        while true {
            try check(epoch)
            guard let mutation = try await store.prepareNextMutation(deviceID: identity.deviceID, execution: execution) else { break }
            try check(epoch)
            do {
                let result = try await transport.push(mutation, identity: identity)
                try check(epoch)
                guard result.items.count == 1, let item = result.items.first,
                      item.operationID == mutation.operationID else {
                    throw SyncError.protocolViolation("上传回执与冻结操作不匹配")
                }
                switch item.status {
                case .applied:
                    guard let record = item.record, item.reasonCode == nil,
                          record.recordID == mutation.recordID, record.version == mutation.baseVersion + 1 else {
                        throw SyncError.protocolViolation("上传回执与冻结操作不匹配")
                    }
                    try await store.acknowledge(item, execution: execution)
                case .rejected:
                    guard item.record == nil, item.reasonCode == "write_retired" else {
                        throw SyncError.protocolViolation("invalid permanent rejection")
                    }
                    try await store.reject(operationID: item.operationID, reason: "write_retired", execution: execution)
                }
                try check(epoch)
            } catch let error as SyncServerError where error.code == "version_conflict" {
                try check(epoch)
                guard error.statusCode == 409, error.operationID == mutation.operationID,
                      error.current == nil || error.current?.recordID == mutation.recordID else {
                    throw SyncError.protocolViolation("冲突快照与操作不匹配")
                }
                try await store.recordConflict(operationID: mutation.operationID, current: error.current, execution: execution)
                try check(epoch)
            }
        }
        try await pullAll(identity: identity, epoch: epoch, execution: execution)
    }

    private func pullAll(identity: SyncIdentity, epoch: UInt64, execution: SyncExecutionLease) async throws {
        var cursor = try await store.pullCursor()
        try check(epoch)
        while true {
            let page = try await transport.pull(cursor: cursor, identity: identity)
            try check(epoch)
            guard page.nextCursor >= cursor, !page.hasMore || page.nextCursor > cursor else {
                throw SyncError.protocolViolation("拉取游标没有前进")
            }
            try await store.apply(page, execution: execution)
            try check(epoch)
            cursor = page.nextCursor
            if !page.hasMore { break }
        }
    }

    private func requestAutomaticSync() {
        guard !isPaused else { return }
        if automaticTask != nil { requestedAgain = true; return }
        let epoch = generation
        automaticTask = Task { [weak self] in await self?.runAutomatic(epoch: epoch) }
    }

    private func localStoreChanged(_ snapshot: SyncStoreSnapshot) {
        guard snapshot.localChangeSequence > observedLocalChangeSequence else { return }
        observedLocalChangeSequence = snapshot.localChangeSequence
        if snapshot.pendingCount > 0 { requestAutomaticSync() }
    }

    private func runAutomatic(epoch: UInt64) async {
        defer { if generation == epoch { automaticTask = nil } }
        var attempt = 0
        while epoch == generation && !isPaused && !Task.isCancelled {
            requestedAgain = false
            do {
                try await synchronize()
                attempt = 0
                if !requestedAgain { return }
            } catch {
                guard epoch == generation, !isPaused, !Task.isCancelled else { return }
                attempt += 1
                guard attempt < retryPolicy.maximumAttempts, isTransient(error) else {
                    // failed 状态发布后的新外部触发仍有效；失败前合并的请求已在 runCycle 清空。
                    if requestedAgain { attempt = 0; continue }
                    return
                }
                let exponential = min(retryPolicy.maximumDelay, retryPolicy.initialDelay * pow(2, Double(attempt - 1)))
                let jittered = min(retryPolicy.maximumDelay, exponential * Double.random(in: 0.8...1.2))
                let serverDelay = (error as? SyncServerError)?.retryAfter ?? 0
                do {
                    try await updateCounts(epoch: epoch)
                    publish(phase: .waitingForRetry, errorCode: "retry_pending")
                    try await sleep(max(jittered, serverDelay))
                }
                catch { return }
            }
        }
    }

    private func isTransient(_ error: any Error) -> Bool {
        if let server = error as? SyncServerError { return server.statusCode == 429 || (500...599).contains(server.statusCode) }
        guard let network = error as? URLError else { return false }
        return [.timedOut, .networkConnectionLost, .notConnectedToInternet, .cannotConnectToHost,
                .cannotFindHost, .dnsLookupFailed, .resourceUnavailable].contains(network.code)
    }

    private func validate(_ identity: SyncIdentity) throws {
        guard identity.userID == store.scope.userID, !identity.accessToken.isEmpty else { throw SyncError.scopeMismatch }
    }

    private func check(_ epoch: UInt64) throws {
        guard epoch == generation, !isPaused, !Task.isCancelled else { throw CancellationError() }
    }

    private func updateCounts(epoch: UInt64, consumeLocalChanges: Bool = false) async throws {
        let snapshot = try await store.snapshot()
        try check(epoch)
        if consumeLocalChanges {
            observedLocalChangeSequence = max(observedLocalChangeSequence, snapshot.localChangeSequence)
        }
        state = SyncState(phase: state.phase, pendingCount: snapshot.pendingCount, conflictCount: snapshot.conflictCount,
                          lastSuccessfulSync: state.lastSuccessfulSync, errorCode: state.errorCode)
    }

    private func publish(phase: SyncPhase, errorCode: String? = nil, success: Date? = nil) {
        state = SyncState(phase: phase, pendingCount: state.pendingCount, conflictCount: state.conflictCount,
                          lastSuccessfulSync: success ?? state.lastSuccessfulSync, errorCode: errorCode)
        for observer in observers.values { observer.yield(state) }
    }

    private func removeObserver(_ id: UUID) { observers.removeValue(forKey: id) }
}
