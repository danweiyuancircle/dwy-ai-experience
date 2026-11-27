#if os(iOS)
import UserNotifications
import PermissionCore
import PermissionIOS

public extension IOSPermissions {
    /// 通知状态异步读取，不阻塞主线程；options 由宿主按实际通知用途选择。
    static func notifications(options: UNAuthorizationOptions = [.alert, .badge, .sound]) -> PermissionClient {
        let center = UNUserNotificationCenter.current()
        return PermissionClient(id: "ios.notifications.\(options.rawValue)",
                                requestableStates: notificationRequestableStates(options: options), status: {
            switch await center.notificationSettings().authorizationStatus {
            case .notDetermined: .notDetermined
            case .authorized: .authorized
            case .denied: .denied
            case .provisional: .provisional
            case .ephemeral: .ephemeral
            @unknown default: .unknown
            }
        }, request: { _ = try await center.requestAuthorization(options: options) })
    }
}

// 完整通知请求可以升级 provisional；再次申请 provisional 不重复触发。
func notificationRequestableStates(options: UNAuthorizationOptions) -> Set<PermissionState> {
    options.contains(.provisional) ? [.notDetermined] : [.notDetermined, .provisional]
}
#endif
