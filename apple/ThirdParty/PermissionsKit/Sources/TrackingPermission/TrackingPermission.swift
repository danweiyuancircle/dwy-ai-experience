import PermissionsKit

#if !os(watchOS)
import AppTrackingTransparency

public extension Permission {

    static var tracking: TrackingPermission {
        return TrackingPermission()
    }
}

public class TrackingPermission: Permission {
    
    open override var kind: Permission.Kind { .tracking }
    open var usageDescriptionKey: String? { "NSUserTrackingUsageDescription" }
    
    public override var status: Permission.Status {
        switch ATTrackingManager.trackingAuthorizationStatus {
        case .authorized: return .authorized
        case .denied: return .denied
        case .notDetermined: return .notDetermined
        case .restricted : return .restricted
        @unknown default: return .unknown
        }
    }
    
    public override func request(completion: @escaping @MainActor () -> Void) {
        ATTrackingManager.requestTrackingAuthorization { _ in
            Task { @MainActor in
                completion()
            }
        }
    }
}
#endif
