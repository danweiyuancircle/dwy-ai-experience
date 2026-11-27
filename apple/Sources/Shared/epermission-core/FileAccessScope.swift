import Foundation

/// 管理用户所选 URL 的临时访问；不请求完整磁盘访问，不持久保存书签。
public struct FileAccessScope: Sendable {
    private let start: @Sendable (URL) -> Bool
    private let stop: @Sendable (URL) -> Void

    public init() {
        start = { $0.startAccessingSecurityScopedResource() }
        stop = { $0.stopAccessingSecurityScopedResource() }
    }

    init(start: @escaping @Sendable (URL) -> Bool, stop: @escaping @Sendable (URL) -> Void) {
        self.start = start
        self.stop = stop
    }

    /// 容器 URL 可能无需 scope；start 返回 false 时仍执行真实 I/O，由 I/O 返回权限错误。
    public func withAccess<T>(to url: URL, operation: (URL) throws -> T) rethrows -> T {
        let accessed = start(url)
        defer { if accessed { stop(url) } }
        return try operation(url)
    }

    /// scope 覆盖整个异步操作；operation 返回、抛错或取消退出后释放。
    public func withAccess<T>(to url: URL, operation: (URL) async throws -> T) async rethrows -> T {
        let accessed = start(url)
        defer { if accessed { stop(url) } }
        return try await operation(url)
    }
}
