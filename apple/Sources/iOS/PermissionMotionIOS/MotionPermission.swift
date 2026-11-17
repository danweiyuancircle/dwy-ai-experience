#if os(iOS)
import PermissionCore
import PermissionIOS
import PermissionsKit
import MotionPermission
import CoreMotion

public extension IOSPermissions {
    /// 请求Motion权限；宿主须提供系统要求的用途声明，拒绝或受限后不重复申请。
    static var motion: PermissionClient {
        let permission = Permission.motion
        return PermissionClient(id: "ios.motion", status: {
            guard CMMotionActivityManager.isActivityAvailable() else { return .unsupported }
            switch permission.status {
            case .authorized: return .authorized
            case .denied: return .denied
            case .notDetermined: return .notDetermined
            case .notSupported: return .unsupported
            case .restricted: return .restricted
            case .limited: return .limited
            case .unknown: return .unknown
            }
        }, request: {
            try IOSPermissions.validateUsageDescriptions(["NSMotionUsageDescription"])
            let manager = CMMotionActivityManager()
            let now = Date()
            try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
                manager.queryActivityStarting(from: now, to: now, to: .main) { [manager] _, error in
                    // CoreMotion 查询结束前持有 manager，避免授权等待中提前释放。
                    _ = manager
                    if let error { continuation.resume(throwing: error) }
                    else { continuation.resume() }
                }
            }
        })
    }
}
#endif
