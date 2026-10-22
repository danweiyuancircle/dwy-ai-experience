import Foundation
import GRDB
import XCTest
@testable import SyncCore

/// 临时磁盘数据库验证真实事务、重开和操作身份，不模拟持久化层。
final class SyncStoreTests: XCTestCase, @unchecked Sendable {
    struct Note: Codable, Sendable, Equatable { var title: String }
    let schema = SyncSchema<Note>(kind: "note", maxPayloadBytes: 1024) { note in
        guard !note.title.isEmpty, note.title.utf8.count <= 100 else {
            throw SyncError.invalidPayload("title")
        }
    }
    func directory() throws -> URL {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        addTeardownBlock { try FileManager.default.removeItem(at: url) }
        return url
    }
    func scope(_ user: UUID? = UUID()) -> SyncScope {
        SyncScope(backendURL: URL(string: "https://sync.example.com")!, appID: "test", userID: user)
    }
    func testSaveAndFrozenOperationSurviveReopen() async throws {
        let dir = try directory(), account = scope(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let first = try await store.prepareNextMutation(deviceID: device)
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        let saved = try await reopened.document(id: id, using: schema)
        let retry = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertEqual(saved?.payload, Note(title: "one"))
        XCTAssertEqual(first, retry)
        XCTAssertEqual(first?.payload?["kind"], .string("note"))
    }

    func record(_ id: UUID, _ title: String, version: Int64 = 1, cursor: Int64 = 1) -> SyncRecord {
        SyncRecord(recordID: id, version: version, cursor: cursor, deleted: false,
                   payload: ["kind": .string("note"), "title": .string(title)])
    }
    func testInvalidSaveIsAtomicAndScopesAreIsolated() async throws {
        let dir = try directory(), account = scope(), id = UUID()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        do {
            try await store.save(SyncDocument(id: id, payload: Note(title: "")), using: schema)
            XCTFail("拒绝无效正文")
        } catch {}
        let empty = try await store.snapshot()
        XCTAssertEqual(empty.pendingCount, 0)
        try await store.save(SyncDocument(id: id, payload: Note(title: "private")), using: schema)
        let other = try SyncStore(directory: dir, scope: scope(), schemas: [schema.erased])
        let missing = try await other.document(id: id, using: schema)
        XCTAssertNil(missing)
    }
    func testFrozenMutationDoesNotChangeDuringEditAndOldAckPreservesNewRevision() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        try await store.save(SyncDocument(id: id, payload: Note(title: "two")), using: schema)
        let retry = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(first, retry)
        try await store.acknowledge(SyncMutationResult(operationID: first.operationID, record: record(id, "one"), replayed: false))
        let saved = try await store.document(id: id, using: schema)
        let next = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(saved?.payload.title, "two")
        XCTAssertEqual(next?.baseVersion, 1)
        XCTAssertNotEqual(next?.operationID, first.operationID)
        let cursor = try await store.pullCursor()
        XCTAssertEqual(cursor, 0)
    }
    func testUnknownKindRollsBackEntirePullPageAndCursor() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID()
        let bad = SyncRecord(recordID: UUID(), version: 1, cursor: 2, deleted: false, payload: ["kind": .string("unknown")])
        do {
            try await store.apply(SyncPullPage(items: [record(id, "one"), bad], nextCursor: 2, hasMore: false))
            XCTFail("未知模型整页拒绝")
        } catch {}
        let missing = try await store.document(id: id, using: schema)
        let cursor = try await store.pullCursor()
        XCTAssertNil(missing)
        XCTAssertEqual(cursor, 0)
    }
    func testPullMatchingFrozenPayloadRetainsReceiptTracking() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let first = try await store.prepareNextMutation(deviceID: device)
        try await store.apply(SyncPullPage(items: [record(id, "one")], nextCursor: 1, hasMore: false))
        let retry = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(first, retry)
    }
    func testOldReplayDoesNotOverwriteNewerPulledVersion() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        try await store.apply(SyncPullPage(items: [record(id, "remote newer", version: 3, cursor: 3)], nextCursor: 3, hasMore: false))
        try await store.acknowledge(SyncMutationResult(operationID: first.operationID, record: record(id, "one"), replayed: true))
        let saved = try await store.document(id: id, using: schema)
        XCTAssertEqual(saved?.payload.title, "remote newer")
        let snapshot = try await store.snapshot()
        XCTAssertEqual(snapshot.pendingCount, 0)
    }
    func testConflictRetainsBothCandidatesAndTypedResolutionValidates() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID()
        try await store.apply(SyncPullPage(items: [record(id, "base")], nextCursor: 1, hasMore: false))
        try await store.save(SyncDocument(id: id, payload: Note(title: "local")), using: schema)
        try await store.apply(SyncPullPage(items: [record(id, "remote", version: 2, cursor: 2)], nextCursor: 2, hasMore: false))
        let conflicts = try await store.conflicts()
        XCTAssertEqual(conflicts.first?.localPayload?["title"], .string("local"))
        XCTAssertEqual(conflicts.first?.remote?.payload?["title"], .string("remote"))
        do {
            try await store.resolveConflict(recordID: id, payload: Note(title: ""), using: schema)
            XCTFail("合并须复用模型校验")
        } catch {}
        try await store.resolveConflict(recordID: id, payload: Note(title: "merged"), using: schema)
        let mutation = try await store.prepareNextMutation(deviceID: UUID())
        XCTAssertEqual(mutation?.baseVersion, 2)
        XCTAssertEqual(mutation?.payload?["title"], .string("merged"))
    }
    func testDeleteDuringUploadRemainsPendingUntilNewMutation() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        try await store.delete(id: id)
        try await store.acknowledge(SyncMutationResult(operationID: first.operationID, record: record(id, "one"), replayed: false))
        let deletion = try await store.prepareNextMutation(deviceID: device)
        let saved = try await store.document(id: id, using: schema)
        XCTAssertNil(saved)
        XCTAssertEqual(deletion?.deleted, true)
        XCTAssertEqual(deletion?.baseVersion, 1)
        XCTAssertNil(deletion?.payload)
    }
    func testImportReceiptIsAtomicAndIdempotent() async throws {
        let dir = try directory(), account = scope(), id = UUID(), receipt = UUID()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try await store.apply(SyncPullPage(items: [], nextCursor: 0, hasMore: false))
        let docs = [SyncDocument(id: id, payload: Note(title: "guest"))]
        try await store.importDocuments(docs, using: schema, importID: receipt)
        try await store.save(SyncDocument(id: id, payload: Note(title: "edited")), using: schema)
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try await reopened.importDocuments(docs, using: schema, importID: receipt)
        let saved = try await reopened.document(id: id, using: schema)
        XCTAssertEqual(saved?.payload.title, "edited")
        let all = try await reopened.documents(using: schema, limit: 100, offset: 0)
        XCTAssertEqual(all.count, 1)
    }
    func testDeviceRecoveryQuarantinesFrozenOperationAndRetainsLocalContent() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), oldDevice = UUID(), newDevice = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "local")), using: schema)
        let first = try await store.prepareNextMutation(deviceID: oldDevice)
        do {
            _ = try await store.prepareNextMutation(deviceID: newDevice)
            XCTFail("不能换设备重放冻结操作")
        } catch { XCTAssertEqual(error as? SyncError, .identityChanged) }
        try await store.apply(SyncPullPage(items: [], nextCursor: 0, hasMore: false))
        try await store.quarantinePendingOperations(newDeviceID: newDevice)
        let blocked = try await store.prepareNextMutation(deviceID: newDevice)
        XCTAssertNil(blocked)
        let conflicts = try await store.conflicts()
        XCTAssertEqual(conflicts.first?.reason, "device_identity_changed")
        try await store.resolveConflict(recordID: id, resolution: .keepLocal)
        let recovered = try await store.prepareNextMutation(deviceID: newDevice)
        XCTAssertNotEqual(first?.operationID, recovered?.operationID)
        XCTAssertEqual(recovered?.payload?["title"], .string("local"))
    }

    func testCorruptStoredPayloadThrowsInsteadOfReturningEmptyList() async throws {
        let dir = try directory(), account = scope(), id = UUID()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let files = try FileManager.default.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil)
        let path = try XCTUnwrap(files.first { $0.pathExtension == "sqlite" })
        let database = try DatabaseQueue(path: path.path)
        try await database.write { db in
            try db.execute(sql: "UPDATE documents SET body = ?", arguments: [Data("broken".utf8)])
        }
        do {
            _ = try await store.documents(using: schema)
            XCTFail("损坏正文必须报错")
        } catch {}
    }

    func testHigherRemoteCandidateAndNewLocalRevisionBothSurviveOldAck() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        try await store.save(SyncDocument(id: id, payload: Note(title: "local two")), using: schema)
        try await store.apply(SyncPullPage(items: [record(id, "remote three", version: 3, cursor: 3)], nextCursor: 3, hasMore: false))
        try await store.acknowledge(SyncMutationResult(operationID: first.operationID, record: record(id, "one"), replayed: true))
        let saved = try await store.document(id: id, using: schema)
        let conflicts = try await store.conflicts()
        XCTAssertEqual(saved?.payload.title, "local two")
        XCTAssertEqual(conflicts.first?.remote?.version, 3)
        XCTAssertEqual(conflicts.first?.baseline?.version, 1)
        let blocked = try await store.prepareNextMutation(deviceID: device)
        XCTAssertNil(blocked)
    }

    func testVersionConflictResolvesUsingRemoteAndCleanDeletionPropagates() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "local")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        try await store.recordConflict(operationID: first.operationID, current: record(id, "remote"))
        try await store.resolveConflict(recordID: id, resolution: .useRemote)
        let saved = try await store.document(id: id, using: schema)
        XCTAssertEqual(saved?.payload.title, "remote")
        let tombstone = SyncRecord(recordID: id, version: 2, cursor: 2, deleted: true, payload: nil)
        try await store.apply(SyncPullPage(items: [tombstone], nextCursor: 2, hasMore: false))
        let deleted = try await store.document(id: id, using: schema)
        XCTAssertNil(deleted)
        let snapshot = try await store.snapshot()
        XCTAssertEqual(snapshot.pendingCount, 0)
        XCTAssertEqual(snapshot.conflictCount, 0)
    }

    func testImportCollisionAndFailedBatchDoNotSilentlyOverwriteCloud() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), other = UUID(), receipt = UUID()
        try await store.apply(SyncPullPage(items: [record(id, "cloud")], nextCursor: 1, hasMore: false))
        do {
            try await store.importDocuments([SyncDocument(id: other, payload: Note(title: "valid")), SyncDocument(id: id, payload: Note(title: ""))], using: schema, importID: receipt)
            XCTFail("坏导入不能提交部分正文与收据")
        } catch {}
        let missing = try await store.document(id: other, using: schema)
        XCTAssertNil(missing)
        try await store.importDocuments([SyncDocument(id: id, payload: Note(title: "guest"))], using: schema, importID: receipt)
        let conflicts = try await store.conflicts()
        XCTAssertEqual(conflicts.first?.reason, "import_collision")
        XCTAssertEqual(conflicts.first?.remote?.payload?["title"], .string("cloud"))
    }

    func testPayloadSizePaginationAndRegistrationCannotBeBypassed() async throws {
        let strict = SyncSchema<Note>(kind: "note", maxPayloadBytes: 40) { _ in }
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [strict.erased])
        do {
            try await store.save(SyncDocument(id: UUID(), payload: Note(title: String(repeating: "x", count: 100))), using: strict)
            XCTFail("字节上限不能绕过")
        } catch {}
        do {
            _ = try await store.documents(using: strict, limit: 101)
            XCTFail("分页限制不能绕过")
        } catch {}
        let loose = SyncSchema<Note>(kind: "note", maxPayloadBytes: 40) { _ in }
        let validatedStore = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        do {
            try await validatedStore.save(SyncDocument(id: UUID(), payload: Note(title: "")), using: loose)
            XCTFail("重新提供schema不能放宽注册校验")
        } catch {}
    }

    func testObserversSeeOnlyCommittedSnapshot() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let stream = await store.changes()
        var iterator = stream.makeAsyncIterator()
        try await store.save(SyncDocument(id: UUID(), payload: Note(title: "one")), using: schema)
        let snapshot = await iterator.next()
        XCTAssertEqual(snapshot?.pendingCount, 1)
        XCTAssertEqual(snapshot?.changeSequence, 1)
    }

    func testVersionExhaustionDoesNotCreateUnsendableMutation() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID()
        try await store.apply(SyncPullPage(items: [record(id, "last", version: Int64.max)], nextCursor: 1, hasMore: false))
        try await store.save(SyncDocument(id: id, payload: Note(title: "local")), using: schema)
        do {
            _ = try await store.prepareNextMutation(deviceID: UUID())
            XCTFail("版本耗尽必须报错，不能生成会让协调器加一溢出的请求")
        } catch { XCTAssertEqual(error as? SyncError, .protocolViolation("record version exhausted")) }
        let saved = try await store.document(id: id, using: schema)
        XCTAssertEqual(saved?.payload.title, "local")
    }

    func testSemanticallyCorruptTombstoneIsReported() async throws {
        let dir = try directory(), id = UUID()
        let store = try SyncStore(directory: dir, scope: scope(), schemas: [schema.erased])
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let files = try FileManager.default.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil)
        let path = try XCTUnwrap(files.first { $0.pathExtension == "sqlite" })
        let database = try DatabaseQueue(path: path.path)
        try await database.write { db in
            let data = try XCTUnwrap(Data.fetchOne(db, sql: "SELECT body FROM documents"))
            var object = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
            object["deleted"] = true
            try db.execute(sql: "UPDATE documents SET body = ?", arguments: [JSONSerialization.data(withJSONObject: object)])
        }
        do {
            _ = try await store.document(id: id, using: schema)
            XCTFail("损坏墓碑不能折为不存在")
        } catch {}
    }

    func testSchemaKindUsesSameBoundaryAsWireProtocol() throws {
        let accepted = SyncSchema<Note>(kind: String(repeating: "n", count: 128), maxPayloadBytes: 1024) { _ in }
        XCTAssertNoThrow(try SyncStore(directory: directory(), scope: scope(), schemas: [accepted.erased]))
        let invalid = SyncSchema<Note>(kind: "note/other", maxPayloadBytes: 1024) { _ in }
        XCTAssertThrowsError(try SyncStore(directory: directory(), scope: scope(), schemas: [invalid.erased]))
    }

    func testPullCannotAutomaticallyReleaseDeviceRecoveryQuarantine() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), oldDevice = UUID(), newDevice = UUID()
        try await store.apply(SyncPullPage(items: [record(id, "base")], nextCursor: 1, hasMore: false))
        try await store.save(SyncDocument(id: id, payload: Note(title: "local")), using: schema)
        _ = try await store.prepareNextMutation(deviceID: oldDevice)
        try await store.quarantinePendingOperations(newDeviceID: newDevice)
        // 远端回到共同基线也不能代替用户确认恢复旧设备操作。
        try await store.apply(SyncPullPage(items: [record(id, "base", version: 2, cursor: 2)], nextCursor: 2, hasMore: false))
        let pending = try await store.prepareNextMutation(deviceID: newDevice)
        let conflicts = try await store.conflicts()
        XCTAssertNil(pending)
        XCTAssertEqual(conflicts.first?.reason, "device_identity_changed")
        XCTAssertEqual(conflicts.first?.remote?.version, 2)
    }

    func testInvalidatedExecutionCannotCommitPullPage() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let execution = SyncExecutionLease()
        execution.invalidate()
        let id = UUID()
        do {
            try await store.apply(SyncPullPage(items: [record(id, "late")], nextCursor: 1, hasMore: false), execution: execution)
            XCTFail("暂停后的排队页不能落盘")
        } catch { XCTAssertTrue(error is CancellationError) }
        let cursor = try await store.pullCursor()
        let missing = try await store.document(id: id, using: schema)
        XCTAssertEqual(cursor, 0)
        XCTAssertNil(missing)
    }

    func testInvalidatedExecutionCannotAcknowledgeFrozenOperation() async throws {
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "one")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        let execution = SyncExecutionLease()
        execution.invalidate()
        do {
            try await store.acknowledge(SyncMutationResult(operationID: first.operationID, record: record(id, "one"), replayed: false), execution: execution)
            XCTFail("暂停后的回执不能确认冻结请求")
        } catch { XCTAssertTrue(error is CancellationError) }
        let retry = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(retry, first)
    }

    func testConflictCannotChangeRegisteredDocumentKindOrReleaseFrozenOperation() async throws {
        let otherSchema = SyncSchema<Note>(kind: "task", maxPayloadBytes: 1024) { _ in }
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased, otherSchema.erased])
        let id = UUID(), device = UUID()
        try await store.save(SyncDocument(id: id, payload: Note(title: "note")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        let foreign = SyncRecord(recordID: id, version: 1, cursor: 1, deleted: false,
                                 payload: ["kind": .string("task"), "title": .string("other kind")])
        do {
            try await store.recordConflict(operationID: first.operationID, current: foreign)
            XCTFail("同UUID冲突不能改变kind")
        } catch {}
        let retry = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(retry, first)
        let saved = try await store.document(id: id, using: schema)
        XCTAssertEqual(saved?.payload.title, "note")
    }
}
