import Foundation

/// 权限模块所含上游 MIT 声明，供宿主展示或纳入开源许可页面。
public enum PermissionAttributions {
    public static func text() throws -> String {
        guard let url = Bundle.module.url(forResource: "ThirdPartyNotices", withExtension: "txt") else {
            throw CocoaError(.fileNoSuchFile)
        }
        return try String(contentsOf: url, encoding: .utf8)
    }
}
