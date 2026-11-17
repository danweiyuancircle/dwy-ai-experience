import Network
import XCTest
@testable import PermissionCore

/// TCP 探测只把系统明确给出的本地网络拒绝归为权限问题，不凭 POSIX 错误推测。
final class LocalNetworkAccessTests: XCTestCase {
    /// waiting 阶段的 denied 也是系统弹窗未决。这时收口会 cancel 连接，macOS 弹窗不会出现。
    /// 只有连接已经 failed，才是用户拒绝或系统不再弹窗。
    func test_explicitDeniedPath_reportsPermissionDenial() {
        XCTAssertNil(LocalNetworkAccess.result(for: .waiting(.posix(.EHOSTUNREACH)), unsatisfiedReason: .localNetworkDenied))
        XCTAssertEqual(LocalNetworkAccess.result(for: .failed(.posix(.EHOSTUNREACH)), unsatisfiedReason: .localNetworkDenied), .localNetworkDenied)
    }

    /// 短超时碰到未决弹窗必须留下连接。按普通超时 cancel 会把系统权限框一起取消。
    func test_timeoutWhileSystemPromptPending_holdsConnection() {
        XCTAssertEqual(
            LocalNetworkAccess.timeoutAction(state: .waiting(.posix(.EHOSTUNREACH)), unsatisfiedReason: .localNetworkDenied),
            .holdSystemPrompt
        )
        XCTAssertGreaterThanOrEqual(LocalNetworkAccess.systemPromptHold, 10)
    }

    /// 弹窗保留时间过了仍是 denied waiting：视为未允许，这时才可以结束连接并给出设置页。
    func test_promptHoldExpiredWhileStillDenied_finishesAsDenial() {
        XCTAssertEqual(
            LocalNetworkAccess.promptHoldExpiredAction(
                state: .waiting(.posix(.EHOSTUNREACH)),
                unsatisfiedReason: .localNetworkDenied
            ),
            .finish(.localNetworkDenied)
        )
    }

    /// 用户已经点允许、连接还在握手时，保留时间到期也不能按拒绝或关闭掐掉。
    func test_promptHoldExpiredWhilePreparing_leavesConnection() {
        XCTAssertEqual(
            LocalNetworkAccess.promptHoldExpiredAction(state: .preparing, unsatisfiedReason: nil),
            .leave
        )
        XCTAssertEqual(
            LocalNetworkAccess.promptHoldExpiredAction(state: .ready, unsatisfiedReason: nil),
            .finish(.open)
        )
    }

    /// 无路由和端口拒绝不等于权限拒绝；waiting 尚有恢复机会。
    func test_ordinaryConnectionErrors_doNotReportPermissionDenial() {
        XCTAssertNil(LocalNetworkAccess.result(for: .waiting(.posix(.EHOSTUNREACH)), unsatisfiedReason: nil))
        XCTAssertEqual(LocalNetworkAccess.result(for: .failed(.posix(.EHOSTUNREACH)), unsatisfiedReason: nil), .closed)
        XCTAssertEqual(LocalNetworkAccess.result(for: .failed(.posix(.ECONNREFUSED)), unsatisfiedReason: .notAvailable), .closed)
    }

    /// 连接成功或主动取消以连接状态为准，不沿用旧路径上的拒绝原因。
    func test_readyAndCancelled_overrideStaleDeniedPath() {
        XCTAssertEqual(LocalNetworkAccess.result(for: .ready, unsatisfiedReason: .localNetworkDenied), .open)
        XCTAssertEqual(LocalNetworkAccess.result(for: .cancelled, unsatisfiedReason: .localNetworkDenied), .closed)
        XCTAssertNil(LocalNetworkAccess.result(for: .preparing, unsatisfiedReason: .localNetworkDenied))
    }

    /// 端口来自用户或外部数据；超出 UInt16 范围必须返回 closed，不能触发转换 trap。
    func test_invalidPorts_returnClosed() async {
        for port in [Int.min, -1, 0, 65_536, Int.max] {
            let result = await LocalNetworkAccess.probe(host: "127.0.0.1", port: port)
            XCTAssertEqual(result, .closed)
        }
    }

    /// 上层取消重连后探针不得继续等待完整 timeout，也不能把取消当成权限拒绝。
    func test_cancelledTask_returnsClosedWithoutWaitingForTimeout() async {
        let task = Task {
            withUnsafeCurrentTask { $0?.cancel() }
            return await LocalNetworkAccess.probe(host: "192.0.2.1", port: 9, timeout: 30)
        }
        let start = Date()
        let result = await task.value
        XCTAssertEqual(result, .closed)
        XCTAssertLessThan(Date().timeIntervalSince(start), 1)
    }

    /// 首次系统授权弹窗 pending 也会给出 denied，权限页监听必须保留连接等用户选择。
    func test_permissionWait_keepsWaitingForDeniedPath() {
        XCTAssertNil(LocalNetworkAccess.result(for: .waiting(.posix(.EHOSTUNREACH)), unsatisfiedReason: .localNetworkDenied, waitsForLocalNetworkAccess: true))
        XCTAssertEqual(LocalNetworkAccess.result(for: .failed(.posix(.EHOSTUNREACH)), unsatisfiedReason: .localNetworkDenied, waitsForLocalNetworkAccess: true), .localNetworkDenied)
    }

    /// 对端拒绝端口说明请求已通过本地权限检查，权限页应回到正常连接流程处理设备错误。
    func test_permissionWait_portRefusedAllowsNormalConnectionRetry() {
        XCTAssertEqual(LocalNetworkAccess.result(for: .failed(.posix(.ECONNREFUSED)), unsatisfiedReason: nil, waitsForLocalNetworkAccess: true), .open)
        XCTAssertEqual(LocalNetworkAccess.result(for: .waiting(.posix(.ECONNREFUSED)), unsatisfiedReason: .notAvailable, waitsForLocalNetworkAccess: true), .open)
        XCTAssertNil(LocalNetworkAccess.result(for: .waiting(.posix(.ECONNREFUSED)), unsatisfiedReason: .localNetworkDenied, waitsForLocalNetworkAccess: true))
    }

    /// 路径未知时无路由或网络关闭不能证明权限恢复，避免权限页反复自动拨号。
    func test_permissionWait_unknownNetworkFailureDoesNotTriggerRetry() {
        XCTAssertEqual(LocalNetworkAccess.result(for: .failed(.posix(.EHOSTUNREACH)), unsatisfiedReason: nil, waitsForLocalNetworkAccess: true), .closed)
        XCTAssertEqual(LocalNetworkAccess.result(for: .failed(.posix(.ENETDOWN)), unsatisfiedReason: .notAvailable, waitsForLocalNetworkAccess: true), .closed)
        XCTAssertNil(LocalNetworkAccess.result(for: .waiting(.posix(.EHOSTUNREACH)), unsatisfiedReason: nil, waitsForLocalNetworkAccess: true))
    }

    /// 权限页关闭后即使没有定时器，取消任务也必须立即结束监听。
    func test_cancelledPermissionWait_returnsFalse() async {
        let task = Task {
            withUnsafeCurrentTask { $0?.cancel() }
            return await LocalNetworkAccess.waitForLocalNetworkAccess(host: "192.0.2.1", port: 9)
        }
        let result = await task.value
        XCTAssertFalse(result)
    }
}
