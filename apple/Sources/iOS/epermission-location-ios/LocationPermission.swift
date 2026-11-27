#if os(iOS)
import CoreLocation
import PermissionCore
import PermissionIOS

/// 系统定位范围与精度分别返回，精度降低不等同于拒绝定位。
public struct LocationPermissionSnapshot: Sendable {
    public let state: PermissionState
    public let isPrecise: Bool
}

/// 定位 delegate 必须随请求保活；宿主按页面生命周期持有，离开页面可取消等待。
@MainActor
public final class LocationPermission: NSObject, CLLocationManagerDelegate {
    private let manager: CLLocationManager
    private let validateUsageDescriptions: @MainActor ([String]) throws -> Void
    private var pending: CheckedContinuation<PermissionState, Error>?
    private var requesting = false

    public override convenience init() {
        self.init(manager: CLLocationManager(), validateUsageDescriptions: { try IOSPermissions.validateUsageDescriptions($0) })
    }

    init(manager: CLLocationManager, validateUsageDescriptions: @escaping @MainActor ([String]) throws -> Void) {
        self.manager = manager
        self.validateUsageDescriptions = validateUsageDescriptions
        super.init()
        manager.delegate = self
    }

    public var snapshot: LocationPermissionSnapshot {
        LocationPermissionSnapshot(state: Self.state(manager.authorizationStatus),
                                   isPrecise: manager.accuracyAuthorization == .fullAccuracy)
    }

    /// 首次请求等待状态确定；always 升级只发起申请并返回当前状态，宿主随后刷新 snapshot。
    /// 系统保持 whenInUse 时不保证发出 delegate 回调，不能把升级包装成必定完成的等待。
    public func request(always: Bool = false) async throws -> PermissionState {
        try Task.checkCancellation()
        guard !requesting else { throw LocationPermissionError.requestInProgress }
        try validateUsageDescriptions(always
            ? ["NSLocationWhenInUseUsageDescription", "NSLocationAlwaysAndWhenInUseUsageDescription"]
            : ["NSLocationWhenInUseUsageDescription"])
        let current = snapshot.state
        guard current == .notDetermined || (always && current == .whenInUse) else { return current }
        if current == .whenInUse {
            manager.requestAlwaysAuthorization()
            return snapshot.state
        }
        requesting = true
        defer { requesting = false }
        return try await withTaskCancellationHandler {
            try await withCheckedThrowingContinuation { continuation in
                pending = continuation
                if always { manager.requestAlwaysAuthorization() }
                else { manager.requestWhenInUseAuthorization() }
            }
        } onCancel: {
            Task { @MainActor [weak self] in self?.finish(.failure(CancellationError())) }
        }
    }

    /// delegate 回调由 CoreLocation 在创建 manager 的主线程派发。
    nonisolated public func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        Task { @MainActor [weak self] in
            guard let self else { return }
            let state = self.snapshot.state
            guard state != .notDetermined else { return }
            self.finish(.success(state))
        }
    }

    private func finish(_ result: Result<PermissionState, Error>) {
        let continuation = pending
        pending = nil
        continuation?.resume(with: result)
    }

    private static func state(_ status: CLAuthorizationStatus) -> PermissionState {
        switch status {
        case .notDetermined: .notDetermined
        case .restricted: .restricted
        case .denied: .denied
        case .authorizedWhenInUse: .whenInUse
        case .authorizedAlways: .always
        @unknown default: .unknown
        }
    }
}

/// 调用方应等待当前定位授权完成再触发升级。
public enum LocationPermissionError: Error { case requestInProgress }
#endif
