#if os(macOS)
import AppKit
import AVFoundation
import EventKit
import PermissionCore
import PermissionFlow
import PermissionFlowExtendedStatus
import SystemSettingsKit

/// 系统设置引导与授权查询分别处理；fullDiskAccess、localNetwork 无可靠全局查询。
public enum MacPermission: String, Sendable, CaseIterable {
    case accessibility, appManagement, bluetooth, calendars, camera, developerTools, fullDiskAccess
    case inputMonitoring, mediaAppleMusic, microphone, reminders, screenRecording, localNetwork
}

/// 宿主在窗口关闭时调用 closeGuide；打开设置不会触发业务重试或伪造授权成功。
@MainActor
public final class MacPermissions {
    private let controller: PermissionFlowController

    /// 不为显示引导而额外申请辅助功能权限；localeIdentifier 随宿主当前语言传入。
    public init(localeIdentifier: String? = nil) {
        controller = PermissionFlow.makeController(configuration: .init(localeIdentifier: localeIdentifier))
        PermissionFlowExtendedStatus.register()
    }

    /// 读取当前系统状态；unknown 不是拒绝或允许，不能用它跳过真实业务操作校验。
    public func status(for permission: MacPermission) -> PermissionState {
        switch permission {
        case .fullDiskAccess, .localNetwork: return .unknown
        case .camera: return Self.captureState(AVCaptureDevice.authorizationStatus(for: .video))
        case .microphone: return Self.captureState(AVCaptureDevice.authorizationStatus(for: .audio))
        case .calendars: return Self.eventState(EKEventStore.authorizationStatus(for: .event))
        case .reminders: return Self.eventState(EKEventStore.authorizationStatus(for: .reminder))
        default:
            guard let pane = PermissionFlowPane(rawValue: permission.rawValue) else { return .unsupported }
            let provider = PermissionStatusRegistry.provider(for: pane)
            guard provider.capability == .preflightSupported else { return .unknown }
            switch provider.authorizationState() {
            case .granted: return .authorized
            case .notGranted: return .denied
            case .unknown, .checking: return .unknown
            }
        }
    }

    /// 仅相机、麦克风、日历和提醒支持本入口；其他权限通过 openSettings 引导用户操作。
    public func request(_ permission: MacPermission) async throws -> PermissionState {
        guard [.camera, .microphone, .calendars, .reminders].contains(permission) else {
            throw MacPermissionError.requiresSystemSettings(permission)
        }
        let client = PermissionClient(id: "mac.\(permission.rawValue)",
                                      requestableStates: permission == .calendars ? [.notDetermined, .writeOnly] : [.notDetermined],
                                      status: { self.status(for: permission) }, request: {
            switch permission {
            case .camera, .microphone:
                try Self.validate(permission == .camera ? "NSCameraUsageDescription" : "NSMicrophoneUsageDescription")
                _ = await AVCaptureDevice.requestAccess(for: permission == .camera ? .video : .audio)
            case .calendars:
                try Self.validate("NSCalendarsFullAccessUsageDescription")
                _ = try await EKEventStore().requestFullAccessToEvents()
            case .reminders:
                try Self.validate("NSRemindersFullAccessUsageDescription")
                _ = try await EKEventStore().requestFullAccessToReminders()
            default: break
            }
        })
        return try await client.request()
    }

    /// 返回值仅表示系统接受跳转；guidance 为 true 时使用 PermissionFlow 的拖拽引导。
    @discardableResult
    public func openSettings(for permission: MacPermission, guidance: Bool = false) -> Bool {
        if permission == .localNetwork {
            closeGuide()
            return NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_LocalNetwork")!)
        }
        guard let pane = PermissionFlowPane(rawValue: permission.rawValue) else { return false }
        if guidance { return controller.authorize(pane: pane) }
        closeGuide()
        return SystemSettings.open(url: pane.settingsURL)
    }

    /// 页面消失或窗口关闭时显式释放悬浮引导与系统窗口监听。
    public func closeGuide() { controller.closePanel() }

    private static func validate(_ key: String) throws {
        guard let value = Bundle.main.object(forInfoDictionaryKey: key) as? String,
              !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw MacPermissionError.missingUsageDescription(key)
        }
    }

    static func captureState(_ state: AVAuthorizationStatus) -> PermissionState {
        switch state {
        case .authorized: .authorized
        case .notDetermined: .notDetermined
        case .denied: .denied
        case .restricted: .restricted
        @unknown default: .unknown
        }
    }

    static func eventState(_ state: EKAuthorizationStatus) -> PermissionState {
        switch state {
        case .fullAccess, .authorized: .authorized
        case .notDetermined: .notDetermined
        case .denied: .denied
        case .restricted: .restricted
        case .writeOnly: .writeOnly
        @unknown default: .unknown
        }
    }
}

/// 配置不足时在系统 API 前报错；不能以设置页打开成功替代权限申请。
public enum MacPermissionError: Error {
    case requiresSystemSettings(MacPermission)
    case missingUsageDescription(String)
}
#endif
