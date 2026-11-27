#if os(iOS)
import PermissionCore
import PermissionIOS
import PermissionsKit
import TrackingPermission

public extension IOSPermissions {
    /// 请求Tracking权限；宿主须提供系统要求的用途声明，拒绝或受限后不重复申请。
    static var tracking: PermissionClient {
        let permission = Permission.tracking
        return PermissionClient(id: "ios.tracking", status: {
            switch permission.status {
            case .authorized: return .authorized
            case .denied: return .denied
            case .notDetermined: return .notDetermined
            case .notSupported: return .unsupported
            case .restricted: return .restricted
            case .limited: return .limited
            case .unknown: return .unknown
            }
        }, validate: { try IOSPermissions.validateUsageDescriptions(["NSUserTrackingUsageDescription"]) },
        requestCompletion: { completion in permission.request(completion: completion) })
    }
}
#endif
