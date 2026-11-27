#if os(iOS)
import UIKit
import PermissionCore

/// 按权限导入 PermissionCameraIOS 等产品后，通过扩展访问对应的权限入口。
@MainActor
public enum IOSPermissions {
    /// 在触发系统 API 前核对必需文案，防止缺失用途声明导致宿主被系统终止。
    public static func validateUsageDescriptions(_ keys: [String], bundle: Bundle = .main) throws {
        for key in keys {
            guard let value = bundle.object(forInfoDictionaryKey: key) as? String,
                  !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                throw IOSPermissionError.missingUsageDescription(key)
            }
        }
    }
    /// 仅打开当前应用设置；返回 true 代表系统接受跳转，不代表权限已允许。
    @available(iOSApplicationExtension, unavailable)
    public static func openSettings() async -> Bool {
        await UIApplication.shared.open(URL(string: UIApplication.openSettingsURLString)!)
    }
}

/// 宿主配置错误；系统请求返回的原始 Error 另行透传。
public enum IOSPermissionError: Error, Equatable {
    case missingUsageDescription(String)
    case emptyAuthenticationReason
}
#endif
