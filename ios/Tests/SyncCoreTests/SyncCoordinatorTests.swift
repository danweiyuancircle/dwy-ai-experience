import Foundation
import XCTest
@testable import SyncCore

/// 使用真实 SQLite 与受控远端合同，覆盖请求交错而不是只检查调用次数。
final class SyncCoordinatorTests: XCTestCase, @unchecked Sendable {
    private struct Note: Codable, Sendable, Equatable { let text: String }
    private let userID = UUID(uuidString: "11111111-1111-4111-8111-111111111111")!
    private let schema = SyncSchema<Note>(kind: "note", maxPayloadBytes: 512) { value in
        guard !value.text.isEmpty else { throw SyncError.invalidPayload("empty note") }
    }

    private func store(userID: UUID?) throws -> SyncStore {
        try SyncStore(
            directory: FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString),
            scope: SyncScope(backendURL: URL(string: "https://example.com/adbox")!, appID: "adbox", userID: userID),
            schemas: [schema.erased]
        )
    }

    private func coordinator(_ store: SyncStore, _ server: CoordinatorTestServer, deviceID: UUID = UUID()) throws -> SyncCoordinator {
        let identity = SyncIdentity(userID: userID, deviceID: deviceID, accessToken: "test-access")
        return SyncCoordinator(store: store, transport: server, identityProvider: { _ in identity },
                               retryPolicy: try SyncRetryPolicy(maximumAttempts: 3, initialDelay: 0.001, maximumDelay: 0.01))
    }

    func testTwoDevicesPropagateCreateUpdateAndDelete() async throws {
        let server = CoordinatorTestServer()
        let phone = try store(userID: userID), mac = try store(userID: userID)
        let phoneSync = try coordinator(phone, server), macSync = try coordinator(mac, server)
        let id = UUID()
        try await phone.save(SyncDocument(id: id, payload: Note(text: "first")), using: schema)
        try await phoneSync.synchronize()
        try await macSync.synchronize()
        let first = try await mac.document(id: id, using: schema)
        XCTAssertEqual(first?.payload.text, "first")
        try await mac.save(SyncDocument(id: id, payload: Note(text: "second")), using: schema)
        try await macSync.synchronize()
        try await phoneSync.synchronize()
        let second = try await phone.document(id: id, using: schema)
        XCTAssertEqual(second?.payload.text, "second")
        try await phone.delete(id: id)
        try await phoneSync.synchronize()
        try await macSync.synchronize()
        let deleted = try await mac.document(id: id, using: schema)
        XCTAssertNil(deleted)
        let remote = await server.record(id)
        XCTAssertEqual(remote?.version, 3)
        XCTAssertEqual(remote?.deleted, true)
    }

    func testPermanentItemRejectionDoesNotFailCycleOrRetryPausedOperation() async throws {
        let server = CoordinatorTestServer(), store = try store(userID: userID)
        let sync = try coordinator(store, server)
        let retired = UUID(uuidString: "00000000-0000-4000-8000-000000000001")!, other = UUID()
        await server.retire(retired)
        try store.saveLocally(.init(id: retired, payload: Note(text: "retired")), using: schema)
        try store.saveLocally(.init(id: other, payload: Note(text: "accepted")), using: schema)
        try await sync.synchronize()
        try await sync.synchronize()
        let accepted = await server.record(other), attempts = await server.pushAttemptCount()
        XCTAssertEqual(accepted?.payload?["text"], .string("accepted"))
        XCTAssertEqual(attempts, 2)
        let diagnostics = try await store.diagnostics()
        XCTAssertEqual(diagnostics.first?.recordID, retired)
        XCTAssertEqual(diagnostics.first?.reason, "write_retired")
    }

    func testLostResponseReusesFrozenOperationAfterReopeningStore() async throws {
        let server = CoordinatorTestServer()
        await server.dropNextResponse()
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        let scope = SyncScope(backendURL: URL(string: "https://example.com/adbox")!, appID: "adbox", userID: userID)
        let firstStore = try SyncStore(directory: directory, scope: scope, schemas: [schema.erased])
        let device = UUID(), id = UUID()
        try await firstStore.save(SyncDocument(id: id, payload: Note(text: "once")), using: schema)
        do {
            try await coordinator(firstStore, server, deviceID: device).synchronize()
            XCTFail("响应丢失应向显式调用者报告")
        } catch let error as URLError { XCTAssertEqual(error.code, .networkConnectionLost) }
        let reopened = try SyncStore(directory: directory, scope: scope, schemas: [schema.erased])
        try await coordinator(reopened, server, deviceID: device).synchronize()
        let record = await server.record(id)
        let state = try await reopened.snapshot()
        XCTAssertEqual(record?.version, 1)
        XCTAssertEqual(state.pendingCount, 0)
        let operations = await server.receiptCount()
        XCTAssertEqual(operations, 1)
    }

    func testEditDuringUploadSurvivesOldAcknowledgement() async throws {
        let server = CoordinatorTestServer(), gate = CoordinatorGate()
        await server.blockNextResponse(on: gate)
        let store = try store(userID: userID), id = UUID()
        let sync = try coordinator(store, server)
        try await store.save(SyncDocument(id: id, payload: Note(text: "old")), using: schema)
        let task = Task { try await sync.synchronize() }
        await gate.waitForArrival()
        try await store.save(SyncDocument(id: id, payload: Note(text: "new")), using: schema)
        await gate.release()
        try await task.value
        let local = try await store.document(id: id, using: schema)
        let remote = await server.record(id)
        XCTAssertEqual(local?.payload.text, "new")
        XCTAssertEqual(remote?.payload?["text"], .string("new"))
        XCTAssertEqual(remote?.version, 2)
    }

    func testPauseRejectsLateResponseAndKeepsPendingOperation() async throws {
        let server = CoordinatorTestServer(), gate = CoordinatorGate()
        await server.blockNextResponse(on: gate)
        let store = try store(userID: userID), id = UUID()
        let sync = try coordinator(store, server)
        try await store.save(SyncDocument(id: id, payload: Note(text: "pending")), using: schema)
        let task = Task { try await sync.synchronize() }
        await gate.waitForArrival()
        await sync.pause()
        await gate.release()
        do { try await task.value; XCTFail("暂停后的旧响应不能被确认") }
        catch is CancellationError { }
        let snapshot = try await store.snapshot()
        XCTAssertEqual(snapshot.pendingCount, 1)
    }

    func testConcurrentTriggersShareOneExecution() async throws {
        let server = CoordinatorTestServer(), gate = CoordinatorGate()
        await server.blockNextResponse(on: gate)
        let store = try store(userID: userID), id = UUID()
        let sync = try coordinator(store, server)
        try await store.save(SyncDocument(id: id, payload: Note(text: "one")), using: schema)
        let first = Task { try await sync.synchronize() }
        await gate.waitForArrival()
        let second = Task { try await sync.synchronize() }
        await gate.release()
        try await first.value
        try await second.value
        let snapshot = try await store.snapshot()
        let receipts = await server.receiptCount()
        XCTAssertEqual(snapshot.pendingCount, 0)
        XCTAssertEqual(receipts, 1)
    }

    func testVersionConflictPreservesBothVersionsAndOtherDocumentsProgress() async throws {
        let server = CoordinatorTestServer()
        let phone = try store(userID: userID), mac = try store(userID: userID), id = UUID()
        let phoneSync = try coordinator(phone, server), macSync = try coordinator(mac, server)
        try await phone.save(SyncDocument(id: id, payload: Note(text: "base")), using: schema)
        try await phoneSync.synchronize()
        try await macSync.synchronize()
        try await phone.save(SyncDocument(id: id, payload: Note(text: "phone")), using: schema)
        try await mac.save(SyncDocument(id: id, payload: Note(text: "mac")), using: schema)
        let otherID = UUID()
        try await mac.save(SyncDocument(id: otherID, payload: Note(text: "independent")), using: schema)
        try await phoneSync.synchronize()
        try await macSync.synchronize()
        let local = try await mac.document(id: id, using: schema)
        let conflicts = try await mac.conflicts()
        let independent = await server.record(otherID)
        XCTAssertEqual(local?.payload.text, "mac")
        XCTAssertEqual(conflicts.count, 1)
        XCTAssertEqual(conflicts.first?.remote?.payload?["text"], .string("phone"))
        XCTAssertEqual(independent?.payload?["text"], .string("independent"))
    }

    func testQuota409DoesNotCreateContentConflict() async throws {
        let server = CoordinatorTestServer()
        await server.rejectPushes(code: "storage_quota_exceeded", status: 409)
        let store = try store(userID: userID), id = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(text: "keep")), using: schema)
        do { try await coordinator(store, server).synchronize(); XCTFail("配额错误必须上报") }
        catch let error as SyncServerError { XCTAssertEqual(error.code, "storage_quota_exceeded") }
        let snapshot = try await store.snapshot()
        XCTAssertEqual(snapshot.conflictCount, 0)
        XCTAssertEqual(snapshot.pendingCount, 1)
    }

    func test401RefreshesOnceAndKeepsSameIdentityScope() async throws {
        let server = CoordinatorTestServer(), refreshes = CoordinatorRefreshCounter()
        await server.requireFreshToken()
        let store = try store(userID: userID), id = UUID(), device = UUID(), user = userID
        try await store.save(SyncDocument(id: id, payload: Note(text: "authenticated")), using: schema)
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { force in
            if force { await refreshes.increment() }
            return SyncIdentity(userID: user, deviceID: device, accessToken: force ? "fresh" : "expired")
        }, retryPolicy: try SyncRetryPolicy(maximumAttempts: 2, initialDelay: 0.001, maximumDelay: 0.01))
        try await sync.synchronize()
        let count = await refreshes.value
        let snapshot = try await store.snapshot()
        XCTAssertEqual(count, 1)
        XCTAssertEqual(snapshot.pendingCount, 0)
    }

    func testGuestRemainsLocalWithoutRequestingIdentity() async throws {
        let server = CoordinatorTestServer(), store = try store(userID: nil), id = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(text: "guest")), using: schema)
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { _ in
            XCTFail("游客不应请求凭据")
            throw SyncError.scopeMismatch
        }, retryPolicy: try SyncRetryPolicy(maximumAttempts: 1, initialDelay: 0, maximumDelay: 0))
        try await sync.synchronize()
        let local = try await store.document(id: id, using: schema)
        XCTAssertEqual(local?.payload.text, "guest")
    }

    func testWrongAccountCannotUpload() async throws {
        let server = CoordinatorTestServer(), store = try store(userID: userID), id = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(text: "private")), using: schema)
        let wrong = SyncIdentity(userID: UUID(), deviceID: UUID(), accessToken: "wrong")
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { _ in wrong },
                                   retryPolicy: try SyncRetryPolicy(maximumAttempts: 1, initialDelay: 0, maximumDelay: 0))
        do { try await sync.synchronize(); XCTFail("跨账号必须拒绝") }
        catch SyncError.scopeMismatch { }
        let remote = await server.record(id)
        XCTAssertNil(remote)
    }

    func testAutomaticRetryConfirmsLostResponseWithoutNewVersion() async throws {
        let server = CoordinatorTestServer(), store = try store(userID: userID), id = UUID()
        await server.dropNextResponse()
        try await store.save(SyncDocument(id: id, payload: Note(text: "retry")), using: schema)
        let sync = try coordinator(store, server)
        let states = await sync.states()
        let finished = expectation(description: "自动重试后完成同步")
        let observation = Task {
            for await state in states where state.phase == .idle && state.lastSuccessfulSync != nil {
                finished.fulfill(); return
            }
        }
        await sync.start()
        await fulfillment(of: [finished], timeout: 5)
        observation.cancel()
        await sync.pause()
        let remote = await server.record(id)
        let pending = try await store.snapshot()
        XCTAssertEqual(remote?.version, 1)
        XCTAssertEqual(pending.pendingCount, 0)
    }

    func testDefaultRetrySleepCancelsOversizedServerDelay() async throws {
        let server = CoordinatorTestServer(), store = try store(userID: userID)
        await server.rejectPushes(code: "temporarily_unavailable", status: 503, retryAfter: .greatestFiniteMagnitude)
        try await store.save(SyncDocument(id: UUID(), payload: Note(text: "preserve")), using: schema)
        let sync = try coordinator(store, server)
        let states = await sync.states()
        let waiting = expectation(description: "进入默认重试等待")
        let observation = Task {
            for await state in states where state.phase == .waitingForRetry { waiting.fulfill(); return }
        }
        await sync.start()
        await fulfillment(of: [waiting], timeout: 5)
        observation.cancel()
        try await Task.sleep(nanoseconds: 50_000_000)
        let attemptsWhileWaiting = await server.pushAttemptCount()
        XCTAssertEqual(attemptsWhileWaiting, 1, "超长等待不能溢出成负延迟而立即重试")
        await sync.pause()
        let attempts = await server.pushAttemptCount()
        let pending = try await store.snapshot()
        XCTAssertEqual(attempts, 1)
        XCTAssertEqual(pending.pendingCount, 1)
    }

    func testAutomaticRetryHonorsAttemptLimitAndServerDelay() async throws {
        let server = CoordinatorTestServer(), delays = CoordinatorDelayRecorder()
        await server.rejectPushes(code: "temporarily_unavailable", status: 503, retryAfter: 2)
        let store = try store(userID: userID), id = UUID(), user = userID, device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(text: "preserve")), using: schema)
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { _ in
            SyncIdentity(userID: user, deviceID: device, accessToken: "test-access")
        }, retryPolicy: try SyncRetryPolicy(maximumAttempts: 3, initialDelay: 0.01, maximumDelay: 0.1),
        sleep: { duration in await delays.record(duration) })
        let states = await sync.states()
        let finished = expectation(description: "第三次失败后停止重试")
        let observation = Task {
            for await state in states where state.phase == .failed {
                if await server.pushAttemptCount() == 3 { finished.fulfill(); return }
            }
        }
        await sync.start()
        await fulfillment(of: [finished], timeout: 5)
        observation.cancel()
        await sync.pause()
        let attempts = await server.pushAttemptCount()
        let waits = await delays.values
        let pending = try await store.snapshot()
        XCTAssertEqual(attempts, 3)
        XCTAssertEqual(waits, [2, 2])
        XCTAssertEqual(pending.pendingCount, 1)
    }

    func testMismatchedTransportScopeCannotUploadOrApplyRemoteData() async throws {
        let wrongScope = SyncScope(backendURL: URL(string: "https://stage.example.com/other")!, appID: "other", userID: userID)
        let server = CoordinatorTestServer(scope: wrongScope)
        let store = try store(userID: userID), id = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(text: "production data")), using: schema)
        do { try await coordinator(store, server).synchronize(); XCTFail("传输环境和应用错配必须被拒绝") }
        catch SyncError.scopeMismatch { }
        let remote = await server.record(id)
        let snapshot = try await store.snapshot()
        XCTAssertNil(remote)
        XCTAssertEqual(snapshot.pendingCount, 1)
    }

    func testManualSyncPublishesDurablePendingCountsAtStartAndAfterInFlightFailure() async throws {
        let server = CoordinatorTestServer(), gate = CoordinatorGate(), syncing = CoordinatorGate(), store = try store(userID: userID)
        await server.dropNextResponse()
        await server.blockNextResponse(on: gate)
        try store.saveLocally(.init(id: UUID(), payload: Note(text: "first")), using: schema)
        let sync = try coordinator(store, server), states = await sync.states()
        let observed = Task { () -> [SyncState] in
            var values: [SyncState] = []
            for await state in states {
                values.append(state)
                if state.phase == .syncing { await syncing.arriveAndWait() }
                if state.phase == .failed { return values }
            }
            return values
        }
        let operation = Task { try await sync.synchronize() }
        await gate.waitForArrival()
        await syncing.waitForArrival()
        try store.saveLocally(.init(id: UUID(), payload: Note(text: "edited during request")), using: schema)
        await syncing.release()
        await gate.release()
        do { try await operation.value; XCTFail("响应丢失必须反馈") }
        catch let error as URLError { XCTAssertEqual(error.code, .networkConnectionLost) }
        let values = await observed.value, durable = try await store.snapshot()
        XCTAssertEqual(values.first(where: { $0.phase == .syncing })?.pendingCount, 1)
        XCTAssertEqual(values.last?.pendingCount, 2)
        XCTAssertEqual(values.last?.pendingCount, durable.pendingCount)
        XCTAssertEqual(values.last?.conflictCount, durable.conflictCount)
    }

    func testAutomaticRetryWaitingPublishesDurableCountsAndPauseRejectsLateState() async throws {
        let server = CoordinatorTestServer(), response = CoordinatorGate(), retry = CoordinatorGate()
        let store = try store(userID: userID), user = userID, device = UUID()
        await server.dropNextResponse()
        await server.blockNextResponse(on: response)
        try store.saveLocally(.init(id: UUID(), payload: Note(text: "first")), using: schema)
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { _ in
            SyncIdentity(userID: user, deviceID: device, accessToken: "test-access")
        }, retryPolicy: try SyncRetryPolicy(maximumAttempts: 3, initialDelay: 0, maximumDelay: 0),
        sleep: { _ in await retry.arriveAndWait() })
        let states = await sync.states()
        let waiting = Task { () -> SyncState? in
            for await state in states where state.phase == .waitingForRetry { return state }
            return nil
        }
        await sync.start()
        await response.waitForArrival()
        try store.saveLocally(.init(id: UUID(), payload: Note(text: "second")), using: schema)
        await response.release()
        await retry.waitForArrival()
        let state = await waiting.value, durable = try await store.snapshot()
        XCTAssertEqual(state?.pendingCount, 2)
        XCTAssertEqual(state?.pendingCount, durable.pendingCount)
        await sync.pause()
        await retry.release()
        let latest = await sync.states()
        var iterator = latest.makeAsyncIterator()
        let paused = await iterator.next()
        XCTAssertEqual(paused?.phase, .paused)
        XCTAssertEqual(paused?.pendingCount, 2)
    }

    func testIdentityFailurePublishesExistingConflictAndPendingCounts() async throws {
        let store = try store(userID: userID), server = CoordinatorTestServer(), id = UUID()
        let initial = SyncRecord(recordID: id, version: 1, cursor: 1, deleted: false,
                                 payload: ["kind": .string("note"), "text": .string("base")])
        try await store.apply(.init(items: [initial], nextCursor: 1, hasMore: false))
        try store.saveLocally(.init(id: id, payload: Note(text: "local")), using: schema)
        let remote = SyncRecord(recordID: id, version: 2, cursor: 2, deleted: false,
                                payload: ["kind": .string("note"), "text": .string("remote")])
        try await store.apply(.init(items: [remote], nextCursor: 2, hasMore: false))
        try store.saveLocally(.init(id: UUID(), payload: Note(text: "pending")), using: schema)
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { _ in throw URLError(.notConnectedToInternet) },
                                   retryPolicy: try SyncRetryPolicy(maximumAttempts: 1, initialDelay: 0, maximumDelay: 0))
        do { try await sync.synchronize(); XCTFail("离线身份错误必须反馈") }
        catch let error as URLError { XCTAssertEqual(error.code, .notConnectedToInternet) }
        var iterator = await sync.states().makeAsyncIterator()
        let state = await iterator.next(), durable = try await store.snapshot()
        XCTAssertEqual(state?.phase, .failed)
        XCTAssertEqual(state?.pendingCount, 1)
        XCTAssertEqual(state?.conflictCount, 1)
        XCTAssertEqual(state?.pendingCount, durable.pendingCount)
        XCTAssertEqual(state?.conflictCount, durable.conflictCount)
    }
}

/// 模拟响应丢失、迟到与认证；真实版本检查与幂等结果由内存状态保存。
private actor CoordinatorTestServer: SyncTransport {
    nonisolated let scope: SyncScope
    private var records: [UUID: SyncRecord] = [:]
    private var receipts: [UUID: SyncMutationResult] = [:]
    private var cursor: Int64 = 0
    private var drop = false
    private var gate: CoordinatorGate?
    private var rejection: SyncServerError?
    private var freshTokenRequired = false
    private var pushAttempts = 0
    private var retired: UUID?

    init(scope: SyncScope = SyncScope(backendURL: URL(string: "https://example.com/adbox")!, appID: "adbox", userID: UUID(uuidString: "11111111-1111-4111-8111-111111111111")!)) {
        self.scope = scope
    }

    func dropNextResponse() { drop = true }
    func blockNextResponse(on gate: CoordinatorGate) { self.gate = gate }
    func rejectPushes(code: String, status: Int, retryAfter: TimeInterval? = nil) {
        rejection = SyncServerError(statusCode: status, code: code, message: "controlled rejection", operationID: nil, current: nil, retryAfter: retryAfter)
    }
    func requireFreshToken() { freshTokenRequired = true }
    func retire(_ recordID: UUID) { retired = recordID }
    func record(_ id: UUID) -> SyncRecord? { records[id] }
    func receiptCount() -> Int { receipts.count }
    func pushAttemptCount() -> Int { pushAttempts }

    func push(_ mutation: SyncMutation, identity: SyncIdentity) async throws -> SyncPushResult {
        pushAttempts += 1
        if let rejection { throw rejection }
        if retired == mutation.recordID {
            return SyncPushResult(items: [.init(operationID: mutation.operationID, rejectedReason: "write_retired", replayed: false)], cursor: cursor)
        }
        if let receipt = receipts[mutation.operationID] {
            return SyncPushResult(items: [SyncMutationResult(operationID: receipt.operationID, record: receipt.record!, replayed: true)], cursor: cursor)
        }
        guard (records[mutation.recordID]?.version ?? 0) == mutation.baseVersion else {
            throw SyncServerError(statusCode: 409, code: "version_conflict", message: "controlled conflict", operationID: mutation.operationID, current: records[mutation.recordID])
        }
        cursor += 1
        let record = SyncRecord(recordID: mutation.recordID, version: mutation.baseVersion + 1, cursor: cursor,
                                deleted: mutation.deleted, payload: mutation.payload)
        records[mutation.recordID] = record
        let result = SyncMutationResult(operationID: mutation.operationID, record: record, replayed: false)
        receipts[mutation.operationID] = result
        if let gate { self.gate = nil; await gate.arriveAndWait() }
        if drop { drop = false; throw URLError(.networkConnectionLost) }
        return SyncPushResult(items: [result], cursor: cursor)
    }

    func pull(cursor: Int64, identity: SyncIdentity) async throws -> SyncPullPage {
        if freshTokenRequired && identity.accessToken != "fresh" {
            throw SyncServerError(statusCode: 401, code: "unauthorized", message: "expired", operationID: nil, current: nil)
        }
        let items = records.values.filter { $0.cursor > cursor }.sorted { $0.cursor < $1.cursor }
        return SyncPullPage(items: items, nextCursor: self.cursor, hasMore: false)
    }
}

/// 不依赖 sleep 的确定性交错点，模拟不响应取消的迟到网络回调。
private actor CoordinatorGate {
    private var arrived = false
    private var waiter: CheckedContinuation<Void, Never>?
    private var blocked: CheckedContinuation<Void, Never>?
    func arriveAndWait() async {
        arrived = true
        waiter?.resume(); waiter = nil
        await withCheckedContinuation { blocked = $0 }
    }
    func waitForArrival() async {
        if arrived { return }
        await withCheckedContinuation { waiter = $0 }
    }
    func release() { blocked?.resume(); blocked = nil }
}

/// 记录强制刷新次数，身份提供器仍由真实协调器控制。
private actor CoordinatorRefreshCounter {
    private(set) var value = 0
    func increment() { value += 1 }
}

/// 用可注入时钟记录真实退避决策，测试不等待墙钟时间。
private actor CoordinatorDelayRecorder {
    private(set) var values: [TimeInterval] = []
    func record(_ duration: TimeInterval) { values.append(duration) }
}
