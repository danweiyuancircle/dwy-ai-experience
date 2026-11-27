#if os(iOS)
import EventKit
import PermissionCore
import PermissionIOS

public extension IOSPermissions {
    /// 提醒事项仅申请完整访问；系统错误直接传给宿主。
    static var reminders: PermissionClient {
        PermissionClient(id: "ios.reminders", status: {
            switch EKEventStore.authorizationStatus(for: .reminder) {
            case .notDetermined: .notDetermined
            case .fullAccess, .authorized: .authorized
            case .denied: .denied
            case .restricted: .restricted
            case .writeOnly: .writeOnly
            @unknown default: .unknown
            }
        }, request: {
            try validateUsageDescriptions(["NSRemindersFullAccessUsageDescription"])
            _ = try await EKEventStore().requestFullAccessToReminders()
        })
    }
}
#endif
