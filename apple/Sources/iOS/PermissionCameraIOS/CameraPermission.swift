#if os(iOS)
import PermissionCore
import PermissionIOS
import PermissionsKit
import CameraPermission

public extension IOSPermissions {
    /// 请求Camera权限；宿主须提供系统要求的用途声明，拒绝或受限后不重复申请。
    static var camera: PermissionClient {
        let permission = Permission.camera
        return PermissionClient(id: "ios.camera", status: {
            switch permission.status {
            case .authorized: return .authorized
            case .denied: return .denied
            case .notDetermined: return .notDetermined
            case .notSupported: return .unsupported
            case .restricted: return .restricted
            case .limited: return .limited
            case .unknown: return .unknown
            }
        }, validate: { try IOSPermissions.validateUsageDescriptions(["NSCameraUsageDescription"]) },
        requestCompletion: { completion in permission.request(completion: completion) })
    }
}
#endif
