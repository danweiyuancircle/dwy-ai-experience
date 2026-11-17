import Foundation

/// 授权状态不等同于业务操作可执行；limited、writeOnly 等仍需宿主判断实际资源范围。
public enum PermissionState: String, Sendable, Equatable, CaseIterable {
    case notDetermined, authorized, denied, restricted, limited, provisional, ephemeral
    case writeOnly, whenInUse, always, unknown, unsupported
}

/// 基于系统状态的权限入口；宿主只应在用户触发功能时请求，不缓存授权结论。
@MainActor
public struct PermissionClient {
    public let id: String
    private let readStatus: @MainActor () async throws -> PermissionState
    private let performRequest: @MainActor () async throws -> Void
    private let requestableStates: Set<PermissionState>
    private static var requests: [String: Task<Void, Error>] = [:]

    /// 同一 id 必须表示同一种权限与申请范围；例如日历读写和只写必须使用不同 id。
    public init(id: String, requestableStates: Set<PermissionState> = [.notDetermined],
                status: @escaping @MainActor () async throws -> PermissionState,
                request: @escaping @MainActor () async throws -> Void) {
        self.id = id
        self.requestableStates = requestableStates
        readStatus = status
        performRequest = request
    }

    /// 每次读取系统状态；从设置返回时调用，不因打开设置成功就推断授权成功。
    public func status() async throws -> PermissionState { try await readStatus() }

    /// 适配仅报告完成的系统接口；首个回调生效，结果仍通过 status 重新读取。
    public init(id: String, status: @escaping @MainActor () async throws -> PermissionState,
                validate: @escaping @MainActor () throws -> Void = {},
                requestCompletion: @escaping @MainActor (@escaping @MainActor () -> Void) -> Void) {
        self.init(id: id, status: status, request: {
            try validate()
            await withCheckedContinuation { continuation in
                var completed = false
                requestCompletion {
                    guard !completed else { return }
                    completed = true
                    continuation.resume()
                }
            }
        })
    }

    /// 同范围请求合并。系统弹框不能由 Task.cancel 关闭；取消的等待者不会返回业务成功。
    public func request() async throws -> PermissionState {
        try Task.checkCancellation()
        if let existing = Self.requests[id] {
            try await existing.value
            try Task.checkCancellation()
            return try await status()
        }
        let current = try await status()
        try Task.checkCancellation()
        // status 可能挂起；恢复后重新检查，避免两个调用同时创建系统请求。
        if let existing = Self.requests[id] {
            try await existing.value
        } else if requestableStates.contains(current) {
            let task = Task { @MainActor in try await performRequest() }
            Self.requests[id] = task
            defer { Self.requests[id] = nil }
            try await task.value
        } else {
            return current
        }
        try Task.checkCancellation()
        return try await status()
    }
}
