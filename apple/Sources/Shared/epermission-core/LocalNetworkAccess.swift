import Foundation
import Network

/// 探测 TCP 可达性，并保留系统明确给出的本地网络权限拒绝原因。
public enum LocalNetworkAccess {
    /// closed 包括连接失败、超时与取消；只有系统路径明确拒绝本地网络才返回 localNetworkDenied。
    public enum Result: Equatable, Sendable {
        case open
        case closed
        case localNetworkDenied
    }

    /// 尝试在 `timeout` 秒内建立到 `host:port` 的 TCP 连接。
    /// - Returns: 端口开放（连接 ready）返回 true；权限拒绝、超时、失败或取消均返回 false。
    public static func isOpen(host: String, port: Int, timeout: TimeInterval = 2) async -> Bool {
        await probe(host: host, port: port, timeout: timeout) == .open
    }

    /// 给用户点系统本地网络对话框的时间。普通端口超时（0.4s）不算在内。
    ///
    /// macOS 把未决弹窗和已拒绝都报成 `localNetworkDenied`，并且弹窗挂在当前这条
    /// `NWConnection` 上。短超时一到就 cancel，对话框不会出现。10 秒只够点一下，
    /// 读完说明再点允许会把弹窗掐掉，所以这里留 20 秒。
    public static let systemPromptHold: TimeInterval = 20

    /// 短超时碰到未决系统弹窗时的动作。`holdSystemPrompt` 期间禁止 finish / cancel。
    public enum TimeoutAction: Equatable, Sendable {
        /// 结束这次探测，并取消连接。
        case finish(Result)
        /// 系统权限框还挂在这条连接上。
        case holdSystemPrompt
        /// 用户已允许，连接仍在握手。调用方不得按超时收口。
        case leave
    }

    /// 单次探测不缓存权限结论；用户处理系统弹窗或修改权限后，下次探测重新读取系统路径。
    /// - Parameters:
    ///   - host: 目标主机名或 IP。
    ///   - port: 用户或设备提供的 TCP 端口，仅接受 1...65535。
    ///   - timeout: 普通不可达的等待秒数。进入本地网络弹窗未决后改走 `systemPromptHold`，不计入这次超时。
    public static func probe(host: String, port: Int, timeout: TimeInterval = 2) async -> Result {
        await probe(host: host, port: port, timeout: timeout, waitsForLocalNetworkAccess: false)
    }

    /// 权限提示页保留连接等系统授权生效；页面关闭时须取消 Task，避免无限等待。
    /// 返回 true 只说明权限不再阻断；目标端口拒绝仍交给正常连接流程处理。
    public static func waitForLocalNetworkAccess(host: String, port: Int) async -> Bool {
        await probe(host: host, port: port, timeout: nil, waitsForLocalNetworkAccess: true) == .open
    }

    /// 普通探测带超时，权限监听保留 waiting 连接；两种模式共享取消与单次恢复约束。
    private static func probe(host: String, port: Int, timeout: TimeInterval?, waitsForLocalNetworkAccess: Bool) async -> Result {
        guard !Task.isCancelled,
              (1...65_535).contains(port),
              let nwPort = NWEndpoint.Port(rawValue: UInt16(port)) else { return .closed }
        let conn = NWConnection(host: NWEndpoint.Host(host), port: nwPort, using: .tcp)
        let queue = DispatchQueue(label: "appleappkit.local-network")
        let resumer = OneShotProbeResult()
        return await withTaskCancellationHandler {
            await withCheckedContinuation { cont in
                guard resumer.install(cont) else { return }
                // 监听可长期等待授权；弱引用避免连接与其 handler 互相持有。
                conn.stateUpdateHandler = { [weak conn] state in
                    guard let conn else { return }
                    if let result = result(for: state, unsatisfiedReason: conn.currentPath?.unsatisfiedReason,
                                           waitsForLocalNetworkAccess: waitsForLocalNetworkAccess) {
                        resumer.finish(result)
                        conn.cancel()
                    }
                }
                // waiting 通知先于路径更新时，仍须识别随后到达的明确权限拒绝。
                conn.pathUpdateHandler = { [weak conn] path in
                    guard let conn else { return }
                    if let result = result(for: conn.state, unsatisfiedReason: path.unsatisfiedReason,
                                           waitsForLocalNetworkAccess: waitsForLocalNetworkAccess) {
                        resumer.finish(result)
                        conn.cancel()
                    }
                }
                if let timeout {
                    queue.asyncAfter(deadline: .now() + timeout) {
                        let action = timeoutAction(
                            state: conn.state,
                            unsatisfiedReason: conn.currentPath?.unsatisfiedReason
                        )
                        switch action {
                        case .holdSystemPrompt:
                            // 弹窗未决。再留 systemPromptHold，期间 state handler 仍可在用户点允许后收口。
                            queue.asyncAfter(deadline: .now() + systemPromptHold) {
                                let expired = promptHoldExpiredAction(
                                    state: conn.state,
                                    unsatisfiedReason: conn.currentPath?.unsatisfiedReason
                                )
                                guard case let .finish(result) = expired else { return }
                                resumer.finish(result)
                                conn.cancel()
                            }
                        case .finish(let result):
                            resumer.finish(result)
                            conn.cancel()
                        case .leave:
                            break
                        }
                    }
                }
                conn.start(queue: queue)
            }
        } onCancel: {
            resumer.finish(.closed)
            conn.cancel()
        }
    }

    /// 明确 denied 优先；恢复监听仅在连接就绪或对端明确拒绝端口时放行，无路由不能证明授权恢复。
    static func result(for state: NWConnection.State, unsatisfiedReason: NWPath.UnsatisfiedReason?,
                       waitsForLocalNetworkAccess: Bool = false) -> Result? {
        switch state {
        case .ready:
            return .open
        case .cancelled:
            return .closed
        case .waiting(let error):
            // 首次授权弹窗未决也会标 denied。不论短探测还是权限页监听，cancel 都会把系统弹窗一起取消。
            if unsatisfiedReason == .localNetworkDenied {
                return nil
            }
            // 关闭或漂移的 ADB 口也可能保持 waiting；明确端口拒绝足以结束权限监听。
            if waitsForLocalNetworkAccess, error == .posix(.ECONNREFUSED) { return .open }
            return nil
        case .failed(let error):
            if unsatisfiedReason == .localNetworkDenied { return .localNetworkDenied }
            if waitsForLocalNetworkAccess, error == .posix(.ECONNREFUSED) { return .open }
            return .closed
        default:
            return nil
        }
    }

    /// 普通超时到期后的动作。未决弹窗必须留下连接。
    ///
    /// - Parameters:
    ///   - state: 到期时的连接状态。
    ///   - unsatisfiedReason: 到期时路径给出的原因。没有路径时为 nil。
    public static func timeoutAction(
        state: NWConnection.State,
        unsatisfiedReason: NWPath.UnsatisfiedReason?
    ) -> TimeoutAction {
        if case .waiting = state, unsatisfiedReason == .localNetworkDenied {
            return .holdSystemPrompt
        }
        if case .ready = state {
            return .finish(.open)
        }
        if unsatisfiedReason == .localNetworkDenied {
            return .finish(.localNetworkDenied)
        }
        return .finish(.closed)
    }

    /// `systemPromptHold` 到期后的收口。仍停在弹窗未决才判未允许；握手中不掐。
    ///
    /// - Parameters:
    ///   - state: 保留时间结束时的连接状态。
    ///   - unsatisfiedReason: 当时的路径原因。
    public static func promptHoldExpiredAction(
        state: NWConnection.State,
        unsatisfiedReason: NWPath.UnsatisfiedReason?
    ) -> TimeoutAction {
        if case .preparing = state {
            return .leave
        }
        if case .waiting = state, unsatisfiedReason == .localNetworkDenied {
            return .finish(.localNetworkDenied)
        }
        return timeoutAction(state: state, unsatisfiedReason: unsatisfiedReason)
    }
}

/// 串行裁决连接回调、超时与取消；取消可先于 continuation 安装，只恢复一次。
private final class OneShotProbeResult: @unchecked Sendable {
    /// 由 lock 保护；结束后释放 continuation。
    private var cont: CheckedContinuation<LocalNetworkAccess.Result, Never>?
    /// 记录取消先到的结果，同时阻止后续回调重复恢复。
    private var completedResult: LocalNetworkAccess.Result?
    /// cancellation handler 与 Network 队列可并发进入。
    private let lock = NSLock()

    /// 安装等待者；已被取消时立即恢复，并通知调用方不再启动连接。
    func install(_ continuation: CheckedContinuation<LocalNetworkAccess.Result, Never>) -> Bool {
        lock.lock()
        if let completedResult {
            lock.unlock()
            continuation.resume(returning: completedResult)
            return false
        }
        cont = continuation
        lock.unlock()
        return true
    }

    /// 首个结果生效；锁外恢复，避免恢复任务重入时持锁。
    func finish(_ value: LocalNetworkAccess.Result) {
        lock.lock()
        guard completedResult == nil else { lock.unlock(); return }
        completedResult = value
        let continuation = cont
        cont = nil
        lock.unlock()
        continuation?.resume(returning: value)
    }
}
