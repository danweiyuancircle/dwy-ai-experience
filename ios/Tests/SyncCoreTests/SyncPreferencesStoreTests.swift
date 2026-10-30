import XCTest
@testable import SyncCore

@MainActor
final class SyncPreferencesStoreTests: XCTestCase {
    func testOnlyCommittedSnapshotsApplyAndSameValueAcrossScopesStillApplies() async {
        let store = SyncPreferencesStore(value: "guest", generation: 0)
        var applied: [String] = []
        store.onApply = { value, generation in applied.append("\(generation):\(value)") }
        await store.submit({ _ in throw Failure.disk }, onFailure: { _ in }).value
        XCTAssertEqual(store.value, "guest")
        store.apply("guest", generation: 0)
        store.apply("guest", generation: 1)
        store.apply("old", generation: 0)
        XCTAssertEqual(applied, ["0:guest", "1:guest"])
    }

    func testQueuedOldScopeWriteAndLateFailureCannotReachNewScope() async {
        let store = SyncPreferencesStore(value: "A", generation: 1)
        var release: CheckedContinuation<Void, Never>?
        var started: CheckedContinuation<Void, Never>?
        var writes: [UInt64] = []
        var failures = 0
        let first = store.submit({ generation in
            writes.append(generation)
            await withCheckedContinuation { continuation in
                release = continuation
                started?.resume()
            }
            throw Failure.disk
        }, onFailure: { _ in failures += 1 })
        await withCheckedContinuation { started = $0 }
        let queued = store.submit({ writes.append($0) }, onFailure: { _ in failures += 1 })
        store.apply("B", generation: 2)
        release?.resume()
        await first.value
        await queued.value
        XCTAssertEqual(writes, [1])
        XCTAssertEqual(failures, 0)
        XCTAssertEqual(store.value, "B")
    }

    func testCommandsRemainOrderedAndFailuresAreVisibleInCurrentScope() async {
        let store = SyncPreferencesStore(value: 0, generation: 0)
        var writes: [Int] = []
        var failures = 0
        let first = store.submit({ _ in
            await Task.yield()
            writes.append(1)
            throw Failure.disk
        }, onFailure: { _ in failures += 1 })
        let second = store.submit({ _ in writes.append(2) }, onFailure: { _ in failures += 1 })
        await first.value
        await second.value
        XCTAssertEqual(writes, [1, 2])
        XCTAssertEqual(failures, 1)
        XCTAssertEqual(store.value, 0)
    }

    private enum Failure: Error { case disk }
}
