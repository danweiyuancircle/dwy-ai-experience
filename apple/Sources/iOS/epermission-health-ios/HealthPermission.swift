#if os(iOS)
import HealthKit
import PermissionCore
import PermissionIOS

public extension IOSPermissions {
    /// HealthKit 不公开读取是否获准；此入口只发起指定类型请求，返回不代表读取获准。
    static func requestHealth(read: Set<HKObjectType>, write: Set<HKSampleType>) async throws {
        guard HKHealthStore.isHealthDataAvailable() else { throw HealthPermissionError.unavailable }
        var keys: [String] = []
        if !read.isEmpty { keys.append("NSHealthShareUsageDescription") }
        if !write.isEmpty { keys.append("NSHealthUpdateUsageDescription") }
        try validateUsageDescriptions(keys)
        try await HKHealthStore().requestAuthorization(toShare: write, read: read)
    }

    /// 仅查询某种数据的写入授权；禁止用此结果推断读取授权。
    static func healthWriteStatus(for type: HKObjectType) -> PermissionState {
        guard HKHealthStore.isHealthDataAvailable() else { return .unsupported }
        switch HKHealthStore().authorizationStatus(for: type) {
        case .notDetermined: return .notDetermined
        case .sharingAuthorized: return .authorized
        case .sharingDenied: return .denied
        @unknown default: return .unknown
        }
    }
}

/// 健康数据在当前设备不可用；其他错误保持 HealthKit 原始 Error。
public enum HealthPermissionError: Error { case unavailable }
#endif
