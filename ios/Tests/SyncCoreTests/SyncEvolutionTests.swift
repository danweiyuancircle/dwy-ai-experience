import Foundation
import GRDB
import XCTest
@testable import SyncCore

/// 演进测试使用真实账号磁盘库，覆盖隔离、条件创建和冻结请求恢复。
final class SyncEvolutionTests: XCTestCase, @unchecked Sendable {
    struct Setting: Codable, Sendable { let scope: String; let value: String }

    func schema(allowedID: UUID? = nil) -> SyncSchema<Setting> {
        SyncSchema(kind: "setting", maxPayloadBytes: 2048, managedFields: ["value"], identityFields: ["scope"],
                   conflictPolicy: .localIntent, validateRecord: { id, _ in
            if let allowedID, allowedID != id { throw SyncError.unsupportedRecord }
        }) { setting in
            guard setting.scope == "shared", ["light", "dark"].contains(setting.value) else { throw SyncError.unsupportedRecord }
        }
    }

    func directory() throws -> URL {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        addTeardownBlock { try FileManager.default.removeItem(at: directory) }
        return directory
    }

    func scope() -> SyncScope { SyncScope(backendURL: URL(string: "https://sync.example.com")!, appID: "test", userID: UUID()) }

    private func waitForWriter(_ semaphore: DispatchSemaphore) { semaphore.wait() }

    func record(_ id: UUID, value: String = "light", version: Int64 = 1, extra: String = "retained") -> SyncRecord {
        SyncRecord(recordID: id, version: version, cursor: version, deleted: false,
                   payload: ["kind": .string("setting"), "scope": .string("shared"), "value": .string(value), "future": .string(extra)])
    }

    func testUnsupportedValueAndInstanceArePreservedAcrossReopenWhileCursorAdvances() async throws {
        let dir = try directory(), account = scope(), id = UUID(), unknown = UUID(), wrong = UUID()
        let schema = schema(allowedID: id)
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        let future = SyncRecord(recordID: unknown, version: 1, cursor: 2, deleted: false,
                                payload: ["kind": .string("future"), "value": .integer(2)])
        let wrongRecord = SyncRecord(recordID: wrong, version: 1, cursor: 3, deleted: false, payload: record(wrong).payload)
        try await store.apply(.init(items: [record(id, value: "future-case"), future, wrongRecord], nextCursor: 3, hasMore: false))
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        XCTAssertEqual(try reopened.recordStateLocally(id: id), .unsupported)
        XCTAssertEqual(try reopened.recordStateLocally(id: unknown), .unsupported)
        XCTAssertEqual(try reopened.recordStateLocally(id: wrong), .unsupported)
        XCTAssertThrowsError(try reopened.documentLocally(id: id, using: schema))
        let cursor = try await reopened.pullCursor(), diagnostics = try await reopened.diagnostics()
        XCTAssertEqual(cursor, 3)
        XCTAssertEqual(diagnostics.count, 3)
        XCTAssertFalse(try reopened.initializeLocally(.init(id: id, payload: Setting(scope: "shared", value: "dark")), using: schema))
    }

    func testManagedEditRebasesOnLatestRawAndKeepsFrozenRequestImmutable() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try await store.apply(.init(items: [record(id)], nextCursor: 1, hasMore: false))
        try store.saveLocally(.init(id: id, payload: Setting(scope: "shared", value: "dark")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        XCTAssertEqual(first.payload?["future"], .string("retained"))
        try await store.recordConflict(operationID: first.operationID, current: record(id, version: 2, extra: "newer-field"))
        let rebased = try await store.prepareNextMutation(deviceID: device)
        let next = try XCTUnwrap(rebased)
        XCTAssertEqual(next.payload?["value"], .string("dark"))
        XCTAssertEqual(next.payload?["future"], .string("newer-field"))
        XCTAssertEqual(next.baseVersion, 2)
        XCTAssertNotEqual(next.operationID, first.operationID)
        XCTAssertEqual(first.payload?["future"], .string("retained"))
        try await store.recordConflict(operationID: next.operationID, current: record(id, value: "future-case", version: 3))
        do {
            try await store.resolveConflict(recordID: id, resolution: .keepLocal)
            XCTFail("未识别的远端值不能经冲突入口覆写")
        } catch { XCTAssertEqual(error as? SyncError, .unsupportedRecord) }
    }

    func testInitializationNeverOverridesRemoteTombstoneOrLaterUserEdit() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let document = SyncDocument(id: id, payload: Setting(scope: "shared", value: "dark"))
        XCTAssertThrowsError(try store.initializeLocally(document, using: schema))
        try await store.apply(.init(items: [], nextCursor: 0, hasMore: false))
        XCTAssertTrue(try store.initializeLocally(document, using: schema))
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        let tombstone = SyncRecord(recordID: id, version: 1, cursor: 1, deleted: true, payload: nil)
        try await store.recordConflict(operationID: first.operationID, current: tombstone)
        XCTAssertEqual(try store.recordStateLocally(id: id), .deleted)
        XCTAssertFalse(try store.initializeLocally(document, using: schema))

        let other = UUID(), edited = SyncDocument(id: other, payload: Setting(scope: "shared", value: "dark"))
        XCTAssertTrue(try store.initializeLocally(edited, using: schema))
        let preparation = try await store.prepareNextMutation(deviceID: device)
        let initializing = try XCTUnwrap(preparation)
        try store.saveLocally(.init(id: other, payload: Setting(scope: "shared", value: "light")), using: schema)
        try await store.recordConflict(operationID: initializing.operationID, current: record(other, value: "dark"))
        XCTAssertEqual(try store.documentLocally(id: other, using: schema)?.payload.value, "light")
        let pending = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(pending?.payload?["value"], .string("light"))
    }

    func testUnregisteredFrozenItemPausesAcrossReopenAndAnotherKindStillUploads() async throws {
        struct Other: Codable, Sendable { let value: String }
        let otherSchema = SyncSchema<Other>(kind: "other", maxPayloadBytes: 1024) { _ in }
        let dir = try directory(), account = scope(), device = UUID(), id = UUID(), schema = schema()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased, otherSchema.erased])
        try store.saveLocally(.init(id: id, payload: Setting(scope: "shared", value: "light")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [otherSchema.erased])
        let other = UUID()
        try reopened.saveLocally(.init(id: other, payload: Other(value: "send")), using: otherSchema)
        let next = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertEqual(next?.recordID, other)
        let restored = try SyncStore(directory: dir, scope: account, schemas: [schema.erased, otherSchema.erased])
        let retry = try await restored.prepareNextMutation(deviceID: device)
        if retry?.recordID == id { XCTAssertEqual(retry, frozen) }
        else {
            try await restored.reject(operationID: retry!.operationID, reason: "write_retired")
            let original = try await restored.prepareNextMutation(deviceID: device)
            XCTAssertEqual(original, frozen)
        }
    }

    func testPermanentRejectionIsDurableAndDoesNotBlockOtherRecords() async throws {
        let dir = try directory(), account = scope(), schema = schema(), device = UUID()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try store.saveLocally(.init(id: UUID(), payload: Setting(scope: "shared", value: "light")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        try await store.reject(operationID: first.operationID, reason: "write_retired")
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        let nextID = UUID()
        try reopened.saveLocally(.init(id: nextID, payload: Setting(scope: "shared", value: "dark")), using: schema)
        let next = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertEqual(next?.recordID, nextID)
        let diagnostics = try await reopened.diagnostics()
        XCTAssertEqual(diagnostics.first?.reason, "write_retired")
    }

    func testExplicitUserEditRebasesOnRemoteDeletionAndStopsAfterThreeConflicts() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Setting(scope: "shared", value: "dark")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let first = try XCTUnwrap(prepared)
        try await store.recordConflict(operationID: first.operationID,
                                       current: .init(recordID: id, version: 1, cursor: 1, deleted: true, payload: nil))
        let rebased = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(rebased?.baseVersion, 1)
        XCTAssertEqual(rebased?.deleted, false)
        for version in 2...4 {
            guard let mutation = try await store.prepareNextMutation(deviceID: device) else { break }
            try await store.recordConflict(operationID: mutation.operationID,
                                           current: record(id, version: Int64(version), extra: "new-\(version)"))
        }
        let paused = try await store.prepareNextMutation(deviceID: device)
        let conflicts = try await store.conflicts()
        XCTAssertNil(paused)
        XCTAssertEqual(conflicts.count, 1)
        let diagnostics = try await store.diagnostics()
        XCTAssertEqual(diagnostics.first?.reason, "version_conflict")
    }

    func testUnsupportedSameKindDoesNotShortenTypedPaginationOrLosePreservedRawData() async throws {
        let schema = schema(), directory = try directory(), scope = scope()
        let store = try SyncStore(directory: directory, scope: scope, schemas: [schema.erased])
        let unknown = UUID(uuidString: "00000000-0000-4000-8000-000000000001")!
        let known = UUID(uuidString: "00000000-0000-4000-8000-000000000002")!
        try await store.apply(.init(items: [record(unknown, value: "future-case"), record(known, version: 2)], nextCursor: 2, hasMore: false))
        let page = try await store.documents(using: schema, limit: 1)
        XCTAssertEqual(page.first?.id, known)
        let futureSchema = SyncSchema<Setting>(kind: "setting", maxPayloadBytes: 2048) { _ in }
        let upgraded = try SyncStore(directory: directory, scope: scope, schemas: [futureSchema.erased])
        XCTAssertEqual(try upgraded.documentLocally(id: unknown, using: futureSchema)?.payload.value, "future-case")
    }

    func testInvalidPaginationRollsBackEntirePageAndInitialPullFlag() async throws {
        let schema = schema(), id = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        do {
            try await store.apply(.init(items: [record(id)], nextCursor: 2, hasMore: true))
            XCTFail("中间页游标必须等于最后一项cursor")
        } catch {}
        XCTAssertEqual(try store.recordStateLocally(id: id), .missing)
        XCTAssertFalse(try store.initialPullCompletedLocally())
        let cursor = try await store.pullCursor()
        XCTAssertEqual(cursor, 0)
    }

    func testConcurrentStoreConnectionWaitsForShortWriteTransaction() async throws {
        let schema = schema(), directory = try directory(), account = scope()
        let store = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
        let file = try XCTUnwrap(FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil).first { $0.pathExtension == "sqlite" })
        let other = try DatabaseQueue(path: file.path)
        let entered = DispatchSemaphore(value: 0), release = DispatchSemaphore(value: 0)
        let writer = Task.detached {
            try other.write { db in
                try db.execute(sql: "UPDATE metadata SET body = body WHERE id = 1")
                entered.signal()
                release.wait()
            }
        }
        waitForWriter(entered)
        let releasing = Task.detached {
            try await Task.sleep(for: .milliseconds(100))
            release.signal()
        }
        defer { release.signal() }
        try store.saveLocally(.init(id: UUID(), payload: Setting(scope: "shared", value: "light")), using: schema)
        try await writer.value
        try await releasing.value
    }

    func testInitializationCannotBypassRegisteredValidatorAndNewEditRestartsBoundedRebase() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try await store.apply(.init(items: [], nextCursor: 0, hasMore: false))
        let forged = SyncSchema<Setting>(kind: "setting", maxPayloadBytes: 2048, managedFields: ["value"], identityFields: ["scope"], conflictPolicy: .localIntent) { _ in }
        XCTAssertThrowsError(try store.initializeLocally(.init(id: id, payload: Setting(scope: "shared", value: "future")), using: forged))
        try store.saveLocally(.init(id: id, payload: Setting(scope: "shared", value: "dark")), using: schema)
        for version in 1...4 {
            let prepared = try await store.prepareNextMutation(deviceID: device)
            let mutation = try XCTUnwrap(prepared)
            try await store.recordConflict(operationID: mutation.operationID, current: record(id, version: Int64(version)))
        }
        let blocked = try await store.prepareNextMutation(deviceID: device)
        XCTAssertNil(blocked)
        try store.saveLocally(.init(id: id, payload: Setting(scope: "shared", value: "dark")), using: schema)
        let restarted = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(restarted?.baseVersion, 4)
        XCTAssertEqual(restarted?.payload?["value"], .string("dark"))
    }

    func testDeletionRetainsImmutableIdentityBeforeAndAfterTombstoneAcknowledgmentAcrossReopen() async throws {
        let schema = SyncSchema<Setting>(kind: "setting", maxPayloadBytes: 2048,
                                         managedFields: ["value"], identityFields: ["scope"]) { value in
            guard ["shared", "macos"].contains(value.scope) else { throw SyncError.unsupportedRecord }
        }
        for acknowledged in [false, true] {
            let directory = try directory(), account = scope(), id = UUID(), device = UUID()
            let store = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
            try await store.apply(.init(items: [record(id)], nextCursor: 1, hasMore: false))
            try await store.delete(id: id)
            let prepared = try await store.prepareNextMutation(deviceID: device)
            let deletion = try XCTUnwrap(prepared)
            if acknowledged {
                try await store.acknowledge(.init(operationID: deletion.operationID,
                                                 record: .init(recordID: id, version: 2, cursor: 2, deleted: true, payload: nil), replayed: false))
            }
            let reopened = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
            XCTAssertThrowsError(try reopened.saveLocally(.init(id: id, payload: Setting(scope: "macos", value: "dark")), using: schema))
            XCTAssertEqual(try reopened.recordStateLocally(id: id), .deleted)
            let next = try await reopened.prepareNextMutation(deviceID: device)
            XCTAssertEqual(next, acknowledged ? nil : deletion)
            try reopened.saveLocally(.init(id: id, payload: Setting(scope: "shared", value: "dark")), using: schema)
            XCTAssertEqual(try reopened.documentLocally(id: id, using: schema)?.payload.scope, "shared")
        }
    }

    func testRemovedInstancePausesDirtyAndFrozenLocalDeletionWithoutBaselineAcrossReopen() async throws {
        let schema = schema(), removed = UUID(uuidString: "00000000-0000-4000-8000-000000000001")!
        let supported = UUID(uuidString: "00000000-0000-4000-8000-000000000002")!
        for frozen in [false, true] {
            let directory = try directory(), account = scope(), device = UUID()
            let store = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
            try store.saveLocally(.init(id: removed, payload: Setting(scope: "shared", value: "light")), using: schema)
            try await store.delete(id: removed)
            let original = frozen ? try await store.prepareNextMutation(deviceID: device) : nil
            let restricted = self.schema(allowedID: supported)
            let reopened = try SyncStore(directory: directory, scope: account, schemas: [restricted.erased])
            try reopened.saveLocally(.init(id: supported, payload: Setting(scope: "shared", value: "dark")), using: restricted)
            XCTAssertEqual(try reopened.recordStateLocally(id: removed), .unsupported)
            let next = try await reopened.prepareNextMutation(deviceID: device)
            XCTAssertEqual(next?.recordID, supported)
            let diagnostics = try await reopened.diagnostics()
            XCTAssertEqual(diagnostics.first?.recordID, removed)
            if let next { try await reopened.reject(operationID: next.operationID, reason: "write_retired") }
            let stillPaused = try await reopened.prepareNextMutation(deviceID: device)
            XCTAssertNil(stillPaused)
            let restored = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
            let resumed = try await restored.prepareNextMutation(deviceID: device)
            XCTAssertEqual(resumed?.recordID, removed)
            XCTAssertEqual(resumed?.deleted, true)
            XCTAssertNil(resumed?.payload)
            if frozen { XCTAssertEqual(resumed, original) }
        }
    }

    func testRemoteTombstoneNeedsNoSyntheticPayloadOrSupportedInstance() async throws {
        let id = UUID(), schema = schema(allowedID: UUID())
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try await store.apply(.init(items: [.init(recordID: id, version: 1, cursor: 1, deleted: true, payload: nil)], nextCursor: 1, hasMore: false))
        XCTAssertEqual(try store.recordStateLocally(id: id), .deleted)
        XCTAssertTrue(try store.initialPullCompletedLocally())
        let cursor = try await store.pullCursor()
        XCTAssertEqual(cursor, 1)
    }

    func testImportAfterAcknowledgedDeletionPreservesUnknownFieldsAcrossReopenAndResolution() async throws {
        let directory = try directory(), account = scope(), schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
        try await store.apply(.init(items: [record(id)], nextCursor: 1, hasMore: false))
        try await store.delete(id: id)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let deletion = try XCTUnwrap(prepared)
        try await store.acknowledge(.init(operationID: deletion.operationID,
                                         record: .init(recordID: id, version: 2, cursor: 2, deleted: true, payload: nil), replayed: false))
        try await store.importDocuments([.init(id: id, payload: Setting(scope: "shared", value: "dark"))], using: schema, importID: UUID())
        let reopened = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
        let conflicts = try await reopened.conflicts()
        XCTAssertEqual(conflicts.first?.localPayload?["future"], .string("retained"))
        try await reopened.resolveConflict(recordID: id, resolution: .keepLocal)
        let revival = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertEqual(revival?.payload?["future"], .string("retained"))
        XCTAssertEqual(revival?.payload?["value"], .string("dark"))
        XCTAssertEqual(revival?.baseVersion, 2)
    }

    func testCleanRemoteDeletionOverridesHistoricalUnsupportedValueOrInstance() async throws {
        for removedInstance in [false, true] {
            let directory = try directory(), account = scope(), id = UUID(), schema = schema()
            let store = try SyncStore(directory: directory, scope: account, schemas: [schema.erased])
            try await store.apply(.init(items: [record(id, value: removedInstance ? "light" : "future-case")], nextCursor: 1, hasMore: false))
            let current = removedInstance ? self.schema(allowedID: UUID()) : schema
            let reopened = try SyncStore(directory: directory, scope: account, schemas: [current.erased])
            XCTAssertEqual(try reopened.recordStateLocally(id: id), .unsupported)
            try await reopened.apply(.init(items: [.init(recordID: id, version: 2, cursor: 2, deleted: true, payload: nil)], nextCursor: 2, hasMore: false))
            XCTAssertEqual(try reopened.recordStateLocally(id: id), .deleted)
            XCTAssertNil(try reopened.documentLocally(id: id, using: current))
            let diagnostics = try await reopened.diagnostics(), cursor = try await reopened.pullCursor()
            XCTAssertTrue(diagnostics.isEmpty)
            XCTAssertEqual(cursor, 2)
            let restored = try SyncStore(directory: directory, scope: account, schemas: [current.erased])
            XCTAssertEqual(try restored.recordStateLocally(id: id), .deleted)
        }
    }
}
