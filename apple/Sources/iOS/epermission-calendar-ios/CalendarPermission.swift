#if os(iOS)
import EventKit
import PermissionCore
import PermissionIOS

/// 日历读取与仅写入使用不同申请范围。
public enum CalendarPermissionAccess: String, Sendable { case full, writeOnly }

public extension IOSPermissions {
    /// 保留 writeOnly 状态；需要读取时可以从仅写入升级到完整授权。
    static func calendar(access: CalendarPermissionAccess) -> PermissionClient {
        PermissionClient(id: "ios.calendar.\(access.rawValue)",
                         requestableStates: access == .full ? [.notDetermined, .writeOnly] : [.notDetermined],
                         status: {
            switch EKEventStore.authorizationStatus(for: .event) {
            case .notDetermined: .notDetermined
            case .fullAccess, .authorized: .authorized
            case .writeOnly: .writeOnly
            case .denied: .denied
            case .restricted: .restricted
            @unknown default: .unknown
            }
        }, request: {
            try validateUsageDescriptions([access == .full ? "NSCalendarsFullAccessUsageDescription" : "NSCalendarsWriteOnlyAccessUsageDescription"])
            let store = EKEventStore()
            if access == .full { _ = try await store.requestFullAccessToEvents() }
            else { _ = try await store.requestWriteOnlyAccessToEvents() }
        })
    }
}
#endif
