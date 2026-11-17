import XCTest
import Synchronization
@testable import PermissionCore

@MainActor
final class PermissionCoreTests: XCTestCase {
    func testUpstreamLicenseIsIncludedInBuiltResources() throws {
        let text = try PermissionAttributions.text()
        XCTAssertTrue(text.contains("PermissionsKit"))
        XCTAssertTrue(text.contains("PermissionFlow"))
        XCTAssertTrue(text.contains("Permission is hereby granted"))
    }
    func testDeniedDoesNotRequestAgain() async throws {
        var calls = 0
        let permission = PermissionClient(id: "denied", status: { .denied }, request: { calls += 1 })
        let result = try await permission.request()
        XCTAssertEqual(result, .denied)
        XCTAssertEqual(calls, 0)
    }

    func testRepeatedCompletionOnlyResumesOnce() async throws {
        var granted = false
        let client = PermissionClient(id: "duplicate", status: { granted ? .authorized : .notDetermined },
                                      requestCompletion: { completion in
            granted = true
            completion()
            completion()
        })
        let result = try await client.request()
        XCTAssertEqual(result, .authorized)
    }

    func testExplicitScopeUpgradeCanRequestFromWriteOnly() async throws {
        var state = PermissionState.writeOnly
        let client = PermissionClient(id: "calendar-upgrade", requestableStates: [.notDetermined, .writeOnly],
                                      status: { state }, request: { state = .authorized })
        let result = try await client.request()
        XCTAssertEqual(result, .authorized)
    }

    func testConcurrentClientsShareOneSystemRequest() async throws {
        var calls = 0
        var granted = false
        let make = {
            PermissionClient(id: "camera", status: { granted ? .authorized : .notDetermined }, request: {
                calls += 1
                try await Task.sleep(for: .milliseconds(20))
                granted = true
            })
        }
        let first = make(), second = make()
        async let a = first.request()
        async let b = second.request()
        let results = try await [a, b]
        XCTAssertEqual(results, [.authorized, .authorized])
        XCTAssertEqual(calls, 1)
    }

    func testLimitedAndRestrictedRemainDistinct() async throws {
        for state in [PermissionState.limited, .restricted, .provisional, .ephemeral, .unknown, .unsupported] {
            let permission = PermissionClient(id: state.rawValue, status: { state }, request: { XCTFail() })
            let result = try await permission.request()
            XCTAssertEqual(result, state)
        }
    }

    func testFailureIsPropagatedAndNextRequestCanRetry() async throws {
        enum Failure: Error { case unavailable }
        var calls = 0
        let client = PermissionClient(id: "failing", status: { .notDetermined }, request: {
            calls += 1
            if calls == 1 { throw Failure.unavailable }
        })
        do { _ = try await client.request(); XCTFail() } catch Failure.unavailable {}
        _ = try await client.request()
        XCTAssertEqual(calls, 2)
    }

    func testCancelledCallerDoesNotStartSystemRequest() async {
        let client = PermissionClient(id: "cancelled", status: { .notDetermined }, request: { XCTFail() })
        let task = Task { try await client.request() }
        task.cancel()
        do { _ = try await task.value; XCTFail() } catch is CancellationError {} catch { XCTFail("\(error)") }
    }

    func testCancellationWhileSystemRequestWaitsCannotReturnSuccess() async {
        var completion: CheckedContinuation<Void, Never>?
        let client = PermissionClient(id: "cancel-during-request", status: { .notDetermined }, request: {
            await withCheckedContinuation { completion = $0 }
        })
        let task = Task { try await client.request() }
        while completion == nil { await Task.yield() }
        task.cancel()
        completion?.resume()
        do { _ = try await task.value; XCTFail() } catch is CancellationError {} catch { XCTFail("\(error)") }
    }

    func testScopeEndsWhenOperationThrowsAndContainerURLStillWorks() throws {
        let stopped = Mutex(0)
        enum Failure: Error { case read }
        let scope = FileAccessScope(start: { _ in true }, stop: { _ in stopped.withLock { $0 += 1 } })
        XCTAssertThrowsError(try scope.withAccess(to: URL(fileURLWithPath: "/chosen")) { _ in throw Failure.read })
        XCTAssertEqual(stopped.withLock { $0 }, 1)
        let container = FileAccessScope(start: { _ in false }, stop: { _ in XCTFail() })
        XCTAssertEqual(try container.withAccess(to: URL(fileURLWithPath: "/container")) { _ in 42 }, 42)
    }
}
