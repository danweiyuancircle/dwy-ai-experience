import Foundation
import Network

/// 应用根层传入前后台事件；网络恢复仅在前台触发，不依赖 UIKit、AppKit 或业务页面。
@MainActor
public final class SyncLifecycleDriver {
    private let onForeground: @MainActor @Sendable () async -> Void
    private let onBackground: @MainActor @Sendable () async -> Void
    private let monitor: NWPathMonitor?
    private var isForeground = false
    private var isAvailable: Bool?

    /// 回调应调用当前账号的协调器；monitorNetwork=false 供宿主自管网络事件或确定性测试。
    public init(onForeground: @escaping @MainActor @Sendable () async -> Void,
                onBackground: @escaping @MainActor @Sendable () async -> Void,
                monitorNetwork: Bool = true) {
        self.onForeground = onForeground
        self.onBackground = onBackground
        monitor = monitorNetwork ? NWPathMonitor() : nil
        monitor?.pathUpdateHandler = { [weak self] path in
            let available = path.status == .satisfied
            Task { @MainActor [weak self] in await self?.connectivityChanged(isAvailable: available) }
        }
        monitor?.start(queue: DispatchQueue(label: "SyncCore.connectivity"))
    }

    deinit { monitor?.cancel() }

    /// 可在启动和每次应用回到前台时调用，恢复失败后等待的持久队列。
    public func foreground() async {
        isForeground = true
        await onForeground()
    }

    /// 先标记后台，再交宿主执行有界收尾；此后网络恢复不能重新启动同步。
    public func background() async {
        isForeground = false
        await onBackground()
    }

    /// 只消费首次可用或不可用到可用的边沿；重复状态不会连续重发。
    public func connectivityChanged(isAvailable available: Bool) async {
        let recovered = available && isAvailable != true
        isAvailable = available
        if isForeground && recovered { await onForeground() }
    }
}
