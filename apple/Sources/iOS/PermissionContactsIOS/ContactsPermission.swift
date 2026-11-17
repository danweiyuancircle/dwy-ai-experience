#if os(iOS)
import PermissionCore
import PermissionIOS
import PermissionsKit
import ContactsPermission
import Contacts

public extension IOSPermissions {
    /// 请求Contacts权限；宿主须提供系统要求的用途声明，拒绝或受限后不重复申请。
    static var contacts: PermissionClient {
        let permission = Permission.contacts
        return PermissionClient(id: "ios.contacts", status: {
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
            try IOSPermissions.validateUsageDescriptions(["NSContactsUsageDescription"])
            _ = try await CNContactStore().requestAccess(for: .contacts)
        })
    }
}
#endif
