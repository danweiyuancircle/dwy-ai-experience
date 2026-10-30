import Foundation
import XCTest
@testable import SyncCore

final class SyncRemoteWinsTests: XCTestCase, @unchecked Sendable {
    struct Note: Codable, Sendable { let title: String }

    private func schema(_ policy: SyncConflictPolicy = .remoteWins) -> SyncSchema<Note> {
        SyncSchema(kind: "note", maxPayloadBytes: 2048, managedFields: ["title"], conflictPolicy: policy) {
            guard !$0.title.isEmpty else { throw SyncError.unsupportedRecord }
        }
    }

    private func directory() throws -> URL {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        addTeardownBlock { try FileManager.default.removeItem(at: directory) }
        return directory
    }

    private func scope() -> SyncScope {
        .init(backendURL: URL(string: "https://sync.example.com")!, appID: "test", userID: UUID())
    }

    private func record(_ id: UUID, _ title: String, version: Int64 = 1) -> SyncRecord {
        .init(recordID: id, version: version, cursor: version, deleted: false,
              payload: ["kind": .string("note"), "title": .string(title), "future": .integer(version)])
    }

    private func pull(_ record: SyncRecord, into store: SyncStore) async throws {
        try await store.apply(.init(items: [record], nextCursor: record.cursor, hasMore: false))
    }

    func testPullConflictAdoptsRemoteAndLaterEditUploads() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try await pull(record(id, "base"), into: store)
        try store.saveLocally(.init(id: id, payload: Note(title: "local")), using: schema)
        try await pull(record(id, "remote", version: 2), into: store)
        XCTAssertEqual(try store.documentLocally(id: id, using: schema)?.payload.title, "remote")
        let conflicts = try await store.conflicts(), pending = try await store.prepareNextMutation(deviceID: device)
        XCTAssertTrue(conflicts.isEmpty)
        XCTAssertNil(pending)
        try store.saveLocally(.init(id: id, payload: Note(title: "new edit")), using: schema)
        let upload = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(upload?.baseVersion, 2)
        XCTAssertEqual(upload?.payload?["title"], .string("new edit"))
    }

    func testRemoteVersionOnlyChangePreservesLocalIntent() async throws {
        let schema = schema(), id = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        let baseline = record(id, "base")
        try await pull(baseline, into: store)
        try store.saveLocally(.init(id: id, payload: Note(title: "local")), using: schema)
        let unchanged = SyncRecord(recordID: id, version: 2, cursor: 2, deleted: false, payload: baseline.payload)
        try await pull(unchanged, into: store)
        let next = try await store.prepareNextMutation(deviceID: UUID())
        XCTAssertEqual(next?.baseVersion, 2)
        XCTAssertEqual(next?.payload?["title"], .string("local"))
    }

    func testMissing409SnapshotPreservesDataAsDiagnosticUntilConfirmedRemoteArrives() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "local")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        try await store.recordConflict(operationID: frozen.operationID, current: nil)
        XCTAssertEqual(try store.documentLocally(id: id, using: schema)?.payload.title, "local")
        let conflicts = try await store.conflicts(), diagnostics = try await store.diagnostics()
        XCTAssertTrue(conflicts.isEmpty)
        XCTAssertEqual(diagnostics.first?.reason, "remote_state_missing")
        let pending = try await store.prepareNextMutation(deviceID: device)
        XCTAssertNil(pending)
        try await pull(record(id, "confirmed", version: 2), into: store)
        XCTAssertEqual(try store.documentLocally(id: id, using: schema)?.payload.title, "confirmed")
        let remaining = try await store.diagnostics()
        XCTAssertTrue(remaining.isEmpty)
    }

    func testIdentityChangeKeepsFrozenEvidenceAndIsolatesRecord() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let other = SyncSchema<Note>(kind: "other", maxPayloadBytes: 2048) { _ in }
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased, other.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "local")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        let foreign = SyncRecord(recordID: id, version: 2, cursor: 2, deleted: false,
                                 payload: ["kind": .string("other"), "title": .string("foreign")])
        try await store.recordConflict(operationID: frozen.operationID, current: foreign)
        XCTAssertEqual(try store.recordStateLocally(id: id), .unsupported)
        let conflicts = try await store.conflicts(), next = try await store.prepareNextMutation(deviceID: device)
        XCTAssertTrue(conflicts.isEmpty)
        XCTAssertNil(next)
    }

    func test409ChoosesHighestConfirmedRemoteAndCreatesNoConflict() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "local")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        try await pull(record(id, "latest", version: 3), into: store)
        try await store.recordConflict(operationID: frozen.operationID, current: record(id, "older", version: 2))
        XCTAssertEqual(try store.documentLocally(id: id, using: schema)?.payload.title, "latest")
        let snapshot = try await store.snapshot()
        XCTAssertEqual(snapshot.pendingCount, 0)
        XCTAssertEqual(snapshot.conflictCount, 0)
    }

    func testFrozenRequestSurvivesPullAndReopenUntilReceiptThenRemoteWins() async throws {
        let schema = schema(), id = UUID(), device = UUID(), account = scope(), dir = try directory()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "sent")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        try store.saveLocally(.init(id: id, payload: Note(title: "old offline edit")), using: schema)
        try await pull(record(id, "latest", version: 3), into: store)
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        let replay = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertEqual(replay, frozen)
        let receipt = SyncRecord(recordID: id, version: 1, cursor: 1, deleted: false, payload: frozen.payload)
        try await reopened.acknowledge(.init(operationID: frozen.operationID, record: receipt, replayed: true))
        XCTAssertEqual(try reopened.documentLocally(id: id, using: schema)?.payload.title, "latest")
        let pending = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertNil(pending)
    }

    func testEditAfterNewRemoteCandidateSurvivesOldReceiptAcrossReopen() async throws {
        let schema = schema(), id = UUID(), device = UUID(), account = scope(), dir = try directory()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "sent")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        try await pull(record(id, "remote", version: 3), into: store)
        try store.saveLocally(.init(id: id, payload: Note(title: "new intent")), using: schema)
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        let replay = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertEqual(replay, frozen)
        let receipt = SyncRecord(recordID: id, version: 1, cursor: 1, deleted: false, payload: frozen.payload)
        try await reopened.acknowledge(.init(operationID: frozen.operationID, record: receipt, replayed: true))
        let next = try await reopened.prepareNextMutation(deviceID: device)
        XCTAssertNotEqual(next?.operationID, frozen.operationID)
        XCTAssertEqual(next?.baseVersion, 3)
        XCTAssertEqual(next?.payload?["title"], .string("new intent"))
        XCTAssertEqual(next?.payload?["future"], .integer(3))
    }

    func testNewEditBasedOnRemoteSurvivesOld409ButLosesToNewerRemote() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "sent")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        try await pull(record(id, "remote", version: 3), into: store)
        try store.saveLocally(.init(id: id, payload: Note(title: "new intent")), using: schema)
        try await store.recordConflict(operationID: frozen.operationID, current: record(id, "remote", version: 3))
        let next = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(next?.baseVersion, 3)
        let newOperation = try XCTUnwrap(next)
        try await store.recordConflict(operationID: newOperation.operationID, current: record(id, "newer remote", version: 4))
        XCTAssertEqual(try store.documentLocally(id: id, using: schema)?.payload.title, "newer remote")
    }

    func testRemoteTombstoneWinsAndExplicitLaterEditCanRecreate() async throws {
        let schema = schema(), id = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try await pull(record(id, "base"), into: store)
        try store.saveLocally(.init(id: id, payload: Note(title: "offline")), using: schema)
        try await pull(.init(recordID: id, version: 2, cursor: 2, deleted: true, payload: nil), into: store)
        XCTAssertEqual(try store.recordStateLocally(id: id), .deleted)
        try store.saveLocally(.init(id: id, payload: Note(title: "recreate")), using: schema)
        let next = try await store.prepareNextMutation(deviceID: UUID())
        XCTAssertEqual(next?.baseVersion, 2)
        XCTAssertEqual(next?.deleted, false)
    }

    func testDeleteAfterFrozenRemoteCandidateUsesNewRemoteBase() async throws {
        let schema = schema(), id = UUID(), device = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "sent")), using: schema)
        let prepared = try await store.prepareNextMutation(deviceID: device)
        let frozen = try XCTUnwrap(prepared)
        try await pull(record(id, "remote", version: 3), into: store)
        try await store.delete(id: id)
        try await store.recordConflict(operationID: frozen.operationID, current: record(id, "remote", version: 3))
        let next = try await store.prepareNextMutation(deviceID: device)
        XCTAssertEqual(next?.baseVersion, 3)
        XCTAssertEqual(next?.deleted, true)
    }

    func testUnsupportedRemoteIsRetainedWithoutConflictOrAutomaticUpload() async throws {
        let schema = schema(), id = UUID(), account = scope(), dir = try directory()
        let store = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        try store.saveLocally(.init(id: id, payload: Note(title: "offline")), using: schema)
        try await pull(record(id, "", version: 2), into: store)
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [schema.erased])
        XCTAssertEqual(try reopened.recordStateLocally(id: id), .unsupported)
        let conflicts = try await reopened.conflicts(), next = try await reopened.prepareNextMutation(deviceID: UUID())
        XCTAssertTrue(conflicts.isEmpty)
        XCTAssertNil(next)
        let supported = SyncSchema<Note>(kind: "note", maxPayloadBytes: 2048, managedFields: ["title"], conflictPolicy: .remoteWins) { _ in }
        let upgraded = try SyncStore(directory: dir, scope: account, schemas: [supported.erased])
        XCTAssertEqual(try upgraded.documentLocally(id: id, using: supported)?.payload.title, "")
    }

    func testSwitchingManualConflictToRemoteWinsSettlesPersistedConflict() async throws {
        let manual = schema(.manual), id = UUID(), account = scope(), dir = try directory()
        let store = try SyncStore(directory: dir, scope: account, schemas: [manual.erased])
        try await pull(record(id, "base"), into: store)
        try store.saveLocally(.init(id: id, payload: Note(title: "offline")), using: manual)
        try await pull(record(id, "remote", version: 2), into: store)
        let automatic = schema()
        let reopened = try SyncStore(directory: dir, scope: account, schemas: [automatic.erased])
        XCTAssertEqual(try reopened.documentLocally(id: id, using: automatic)?.payload.title, "remote")
        let conflicts = try await reopened.conflicts()
        XCTAssertTrue(conflicts.isEmpty)
    }

    func testImportCollisionKeepsConfirmedRemoteWithoutDialog() async throws {
        let schema = schema(), id = UUID()
        let store = try SyncStore(directory: directory(), scope: scope(), schemas: [schema.erased])
        try await pull(record(id, "remote"), into: store)
        try await store.importDocuments([.init(id: id, payload: Note(title: "guest"))], using: schema, importID: UUID())
        XCTAssertEqual(try store.documentLocally(id: id, using: schema)?.payload.title, "remote")
        let conflicts = try await store.conflicts()
        XCTAssertTrue(conflicts.isEmpty)
    }
}
