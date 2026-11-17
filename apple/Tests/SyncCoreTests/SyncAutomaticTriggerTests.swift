import Foundation
import XCTest
@testable import SyncCore

final class SyncAutomaticTriggerTests: XCTestCase, @unchecked Sendable {
    struct Note: Codable, Sendable { let text: String }

    func testAwaitedStartImmediatelyFailingPullRunsOnceThenObservesNewLocalEdit() async throws {
        try await checkAwaitedStart(initialPending: false)
    }

    func testAwaitedStartWithPendingSnapshotRunsOnceThenObservesNewLocalEdit() async throws {
        try await checkAwaitedStart(initialPending: true)
    }

    private func checkAwaitedStart(initialPending: Bool) async throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        addTeardownBlock { try FileManager.default.removeItem(at: directory) }
        let scope = SyncScope(backendURL: URL(string: "https://sync.example.com")!, appID: "test", userID: UUID())
        let schema = SyncSchema<Note>(kind: "note", maxPayloadBytes: 1024) { _ in }
        let store = try SyncStore(directory: directory, scope: scope, schemas: [schema.erased])
        let server = FailingTriggerTransport(scope: scope, failPull: !initialPending)
        let user = try XCTUnwrap(scope.userID), device = UUID(), id = UUID()
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { _ in
            .init(userID: user, deviceID: device, accessToken: "test")
        }, retryPolicy: try SyncRetryPolicy(maximumAttempts: 1, initialDelay: 0, maximumDelay: 0))
        if initialPending { try store.saveLocally(.init(id: id, payload: Note(text: "queued")), using: schema) }
        do {
            try await sync.startAndSynchronize()
            XCTFail("立即网络失败必须交还调用者")
        } catch let error as URLError { XCTAssertEqual(error.code, .networkConnectionLost) }
        let unwanted = expectation(description: "可等待启动只执行一轮")
        unwanted.isInverted = true
        await server.observeFailure { unwanted.fulfill() }
        try await store.apply(.init(items: [], nextCursor: 0, hasMore: false))
        await fulfillment(of: [unwanted], timeout: 0.15)
        let firstAttempts = await server.failingAttempts
        XCTAssertEqual(firstAttempts, 1)
        let changed = expectation(description: "后续本地编辑仍自动同步")
        await server.observeFailure { changed.fulfill() }
        try store.saveLocally(.init(id: id, payload: Note(text: "new edit")), using: schema)
        await fulfillment(of: [changed], timeout: 5)
        await sync.pause()
        let finalAttempts = await server.failingAttempts
        XCTAssertEqual(finalAttempts, 2)
    }

    func testSingleAttemptWaitsForNewLocalCommitOrExternalStart() async throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        addTeardownBlock { try FileManager.default.removeItem(at: directory) }
        let scope = SyncScope(backendURL: URL(string: "https://sync.example.com")!, appID: "test", userID: UUID())
        let schema = SyncSchema<Note>(kind: "note", maxPayloadBytes: 1024) { _ in }
        let store = try SyncStore(directory: directory, scope: scope, schemas: [schema.erased])
        let server = FailingTriggerTransport(scope: scope)
        let user = try XCTUnwrap(scope.userID), device = UUID()
        let sync = SyncCoordinator(store: store, transport: server, identityProvider: { _ in
            .init(userID: user, deviceID: device, accessToken: "test")
        }, retryPolicy: try SyncRetryPolicy(maximumAttempts: 1, initialDelay: 0, maximumDelay: 0))
        let id = UUID()
        try store.saveLocally(.init(id: id, payload: Note(text: "queued")), using: schema)
        let states = await sync.states()
        let failed = expectation(description: "单次请求失败")
        let observation = Task {
            for await state in states where state.phase == .failed { failed.fulfill(); return }
        }
        await sync.start()
        await fulfillment(of: [failed], timeout: 5)
        observation.cancel()
        let unwanted = expectation(description: "内部 pull 提交不能重发")
        unwanted.isInverted = true
        await server.observePush { unwanted.fulfill() }
        try await store.apply(.init(items: [], nextCursor: 0, hasMore: false))
        await fulfillment(of: [unwanted], timeout: 0.15)
        await server.observePush(nil)
        let firstAttempts = await server.attempts
        XCTAssertEqual(firstAttempts, 1)
        let retry = expectation(description: "新本地提交触发下一轮")
        await server.observePush { retry.fulfill() }
        try store.saveLocally(.init(id: id, payload: Note(text: "new edit")), using: schema)
        await fulfillment(of: [retry], timeout: 5)
        await server.observePush(nil)
        // 等失败状态落定后，外部 start 仍能触发同一冻结请求。
        let finalStates = await sync.states()
        for await state in finalStates where state.phase == .failed { break }
        let external = expectation(description: "外部 start 触发下一轮")
        await server.observePush { external.fulfill() }
        await sync.start()
        await fulfillment(of: [external], timeout: 5)
        await sync.pause()
        let mutations = await server.mutations
        XCTAssertEqual(mutations.count, 3)
        XCTAssertTrue(mutations.allSatisfy { $0 == mutations.first })
        let snapshot = try await store.snapshot()
        XCTAssertEqual(snapshot.pendingCount, 1)
    }
}

private actor FailingTriggerTransport: SyncTransport {
    nonisolated let scope: SyncScope
    private(set) var mutations: [SyncMutation] = []
    var attempts: Int { mutations.count }
    var failingAttempts: Int { failPull ? pullAttempts : mutations.count }
    private var onPush: (@Sendable () -> Void)?
    private var onFailure: (@Sendable () -> Void)?
    private let failPull: Bool
    private var pullAttempts = 0

    init(scope: SyncScope, failPull: Bool = false) { self.scope = scope; self.failPull = failPull }
    func observePush(_ observer: (@Sendable () -> Void)?) { onPush = observer }
    func observeFailure(_ observer: (@Sendable () -> Void)?) { onFailure = observer }
    func push(_ mutation: SyncMutation, identity: SyncIdentity) async throws -> SyncPushResult {
        mutations.append(mutation)
        onPush?()
        onFailure?()
        throw URLError(.networkConnectionLost)
    }
    func pull(cursor: Int64, identity: SyncIdentity) async throws -> SyncPullPage {
        pullAttempts += 1
        if failPull { onFailure?(); throw URLError(.networkConnectionLost) }
        return .init(items: [], nextCursor: cursor, hasMore: false)
    }
}
