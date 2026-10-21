import Foundation
import Observation

/// 管理应用会话，不自动发请求；启动时显式 restore，业务请求前显式 refresh。
@MainActor
@Observable
public final class AuthSessionStore {
    public private(set) var session: AuthSession?
    public private(set) var isSigningIn = false
    @ObservationIgnored private let backend: any AuthBackend
    @ObservationIgnored private let provider: any GoogleIDTokenProviding
    @ObservationIgnored private let tokenStore: any RefreshTokenStoring
    @ObservationIgnored private let deviceID: UUID
    @ObservationIgnored private let now: () -> Date
    @ObservationIgnored private var generation = 0
    @ObservationIgnored private var refreshTask: Task<Void, Error>?

    public init(backend: any AuthBackend, provider: any GoogleIDTokenProviding, tokenStore: any RefreshTokenStoring, deviceID: UUID, now: @escaping () -> Date = Date.init) {
        self.backend = backend
        self.provider = provider
        self.tokenStore = tokenStore
        self.deviceID = deviceID
        self.now = now
    }

    /// 重复点击不重复弹 Google；退出或后续登录使旧请求失效。
    public func signIn() async throws {
        guard !isSigningIn else { return }
        generation += 1
        let operation = generation
        refreshTask = nil
        isSigningIn = true
        defer { if operation == generation { isSigningIn = false } }
        let idToken = try await provider.signIn()
        guard operation == generation else { throw AuthError.superseded }
        let response = try await backend.authenticate(googleIDToken: idToken, deviceID: deviceID)
        try await install(response, operation: operation)
    }

    /// 冷启动只使用应用 refresh token，不恢复 Google profile 充当已登录状态。
    public func restore() async throws {
        guard try tokenStore.load() != nil else { return }
        try await refresh()
    }

    /// 同时到达的业务请求共享一次刷新，避免一次性 refresh token 被并发消费。
    public func refresh() async throws {
        if let refreshTask { return try await refreshTask.value }
        guard !isSigningIn else { throw AuthError.superseded }
        guard let token = try tokenStore.load() else { throw AuthError.signedOut }
        let operation = generation
        let task = Task { @MainActor in
            do {
                let response = try await backend.refresh(refreshToken: token)
                try await install(response, operation: operation)
            } catch let AuthError.server(code, message) where code == "REFRESH_TOKEN_INVALID" {
                // 永久失效与网络暂不可用分开处理；旧请求不能清掉后续账号。
                guard operation == generation else { throw AuthError.superseded }
                session = nil
                provider.signOut()
                try tokenStore.delete()
                throw AuthError.server(code: code, message: message)
            }
        }
        refreshTask = task
        defer { if operation == generation { refreshTask = nil } }
        try await task.value
    }

    /// 先失效并清理本地，再通知后端；网络失败仍保持退出，错误交宿主提示。
    public func signOut() async throws {
        let accessToken = session?.accessToken
        generation += 1
        refreshTask = nil
        isSigningIn = false
        session = nil
        provider.signOut()
        var storageError: (any Error)?
        do { try tokenStore.delete() } catch { storageError = error }
        // Keychain 删除失败也要尝试撤销；同时失败时保留两份错误供宿主处理。
        if let accessToken {
            do { try await backend.logout(accessToken: accessToken) }
            catch {
                if let storageError { throw AuthCleanupError(operationError: storageError, revocationError: error) }
                throw error
            }
        }
        if let storageError { throw storageError }
    }

    /// 保存 refresh 成功后才公开新会话，存储失败不形成不可恢复的半登录状态。
    private func install(_ response: AuthTokenResponse, operation: Int) async throws {
        guard operation == generation else { try await reject(response, error: AuthError.superseded) }
        do { try tokenStore.save(response.refreshToken) }
        catch {
            session = nil
            try await reject(response, error: error)
        }
        session = AuthSession(accessToken: response.accessToken, expiresAt: now().addingTimeInterval(response.expiresIn), user: response.user)
    }

    /// 已收到新凭据但不能安装时撤销新 access；不取消在途刷新而丢失撤销凭据。
    private func reject(_ response: AuthTokenResponse, error operationError: any Error) async throws -> Never {
        do { try await backend.logout(accessToken: response.accessToken) }
        catch { throw AuthCleanupError(operationError: operationError, revocationError: error) }
        throw operationError
    }
}
