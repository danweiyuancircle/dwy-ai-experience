import Foundation
import Observation

/// 管理应用会话，不自动发请求；启动时显式 restore，业务请求前显式 refresh。
@MainActor
@Observable
public final class AuthSessionStore {
    public private(set) var session: AuthSession?
    public private(set) var isSigningIn = false
    @ObservationIgnored private let backend: any AuthBackend
    @ObservationIgnored private let provider: (any GoogleIDTokenProviding)?
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

    /// 邮箱宿主无需安装 Google SDK；调用无参数 signIn 时会抛配置错误。
    public init(backend: any AuthBackend, tokenStore: any RefreshTokenStoring, deviceID: UUID, now: @escaping () -> Date = Date.init) {
        self.backend = backend
        self.provider = nil
        self.tokenStore = tokenStore
        self.deviceID = deviceID
        self.now = now
    }

    /// 重复点击不重复弹 Google；退出或后续登录使旧请求失效。
    public func signIn() async throws {
        guard let provider else { throw AuthError.invalidConfiguration }
        try await performAuthentication { operation in
            let idToken = try await provider.signIn()
            try checkAuthentication(operation)
            let response = try await backend.authenticate(googleIDToken: idToken, deviceID: deviceID)
            try await install(response, operation: operation)
        }
    }

    /// 先申请目标应用挑战，再呈现系统授权；与邮箱/Google 共用会话和迟到撤销路径。
    public func signInWithApple(provider: any AppleAuthorizationProviding) async throws {
        guard let appleBackend = backend as? any AppleAuthBackend else { throw AuthError.invalidConfiguration }
        try await performAuthentication { operation in
            let challenge = try await appleBackend.createAppleChallenge()
            try checkAuthentication(operation)
            let authorization = try await provider.signIn(nonce: challenge.nonce)
            try checkAuthentication(operation)
            let response = try await appleBackend.authenticate(appleAuthorization: authorization, challengeID: challenge.challengeID, deviceID: deviceID)
            try await install(response, operation: operation)
        }
    }

    /// Apple 等第三方入口沿用会话安装及取消代次，不能绕过本地凭据保护。
    public func signIn(provider: String, credential: String) async throws {
        guard let external = backend as? any ExternalAuthBackend else { throw AuthError.invalidConfiguration }
        guard !isSigningIn else { return }
        generation += 1
        let operation = generation
        refreshTask = nil
        isSigningIn = true
        defer { if operation == generation { isSigningIn = false } }
        let response = try await external.authenticate(provider: provider, credential: credential, deviceID: deviceID)
        try await install(response, operation: operation)
    }

    /// 发码不创建会话；用途与挑战由服务端校验。
    public func sendEmailCode(email: String, purpose: EmailCodePurpose) async throws -> EmailCodeChallenge {
        try await emailBackend().sendEmailCode(email: email, purpose: purpose)
    }

    /// 邮箱与 Google 共用会话安装及迟到回调撤销路径。
    public func signIn(email: String, password: String) async throws {
        let emailBackend = try emailBackend()
        try await performAuthentication { operation in
            let response = try await emailBackend.authenticate(email: email, password: password, deviceID: deviceID)
            try await install(response, operation: operation)
        }
    }

    /// 注册成功立即安装后端返回的会话，不再要求重复登录。
    public func register(email: String, password: String, code: String, challengeID: String) async throws {
        let emailBackend = try emailBackend()
        try await performAuthentication { operation in
            let response = try await emailBackend.register(email: email, password: password, code: code, challengeID: challengeID, deviceID: deviceID)
            do { try await install(response, operation: operation) }
            catch { throw AuthRegistrationError(installationError: error) }
        }
    }

    private func performAuthentication(_ authenticate: (Int) async throws -> Void) async throws {
        guard !isSigningIn else { return }
        try Task.checkCancellation()
        generation += 1
        let operation = generation
        refreshTask = nil
        isSigningIn = true
        defer { if operation == generation { isSigningIn = false } }
        try await authenticate(operation)
    }

    private func checkAuthentication(_ operation: Int) throws {
        guard operation == generation else { throw AuthError.superseded }
        try Task.checkCancellation()
    }

    /// 当前 Apple 账号的管理证明只保留在内存；切号、刷新或取消后不返回过期材料。
    public func prepareAppleReauthentication(provider: any AppleAuthorizationProviding, purpose: AppleReauthenticationPurpose) async throws -> AuthReauthentication {
        guard !isSigningIn else { throw AuthError.superseded }
        guard let appleBackend = backend as? any AppleReauthenticationBackend else { throw AuthError.invalidConfiguration }
        let operation = generation
        try Task.checkCancellation()
        try await refreshIfNeeded()
        guard operation == generation, !isSigningIn, let current = session else { throw AuthError.superseded }
        let challenge = try await appleBackend.createAppleChallenge(purpose: purpose, accessToken: current.accessToken)
        try requireCurrentManagementSession(current, operation: operation)
        try Task.checkCancellation()
        let authorization = try await provider.signIn(nonce: challenge.nonce)
        try requireCurrentManagementSession(current, operation: operation)
        try Task.checkCancellation()
        return .apple(authorization: authorization, challengeID: challenge.challengeID)
    }

    /// 敏感管理总是先刷新当前会话；切号后迟到的挑战不能交给新账号页面。
    public func sendEmailUpdateCode(email: String, reauthentication: AuthReauthentication) async throws -> EmailCodeChallenge {
        guard !isSigningIn else { throw AuthError.superseded }
        let operation = generation
        try await refreshIfNeeded()
        guard operation == generation, !isSigningIn, let current = session else { throw AuthError.superseded }
        let challenge = try await managementBackend().sendEmailUpdateCode(email: email, reauthentication: reauthentication, accessToken: current.accessToken)
        try requireCurrentManagementSession(current, operation: operation)
        return challenge
    }

    /// 后端已轮换所有会话；复用唯一 install 路径保存 refresh，固定当前 userId。
    public func updateEmail(email: String, code: String, challengeID: String, newPassword: String? = nil) async throws {
        let previous = generation
        try await refreshIfNeeded()
        guard previous == generation else { throw AuthError.superseded }
        guard !isSigningIn, let current = session else { throw AuthError.signedOut }
        generation += 1
        let operation = generation
        refreshTask = nil
        isSigningIn = true
        defer { if operation == generation { isSigningIn = false } }
        let response = try await managementBackend().updateEmail(email: email, code: code, challengeID: challengeID, newPassword: newPassword, accessToken: current.accessToken)
        guard response.user.id == current.user.id else { try await reject(response, error: AuthError.invalidResponse) }
        try await install(response, operation: operation)
    }

    /// 管理入口完全使用 SDK 当前会话，不让应用读取或手写 Keychain。
    public func listIdentities() async throws -> [AuthLoginIdentity] {
        guard !isSigningIn else { throw AuthError.superseded }
        let operation = generation
        try await refreshIfNeeded()
        guard operation == generation, !isSigningIn, let current = session else { throw AuthError.superseded }
        let result = try await managementBackend().listIdentities(accessToken: current.accessToken)
        try requireCurrentManagementSession(current, operation: operation)
        return result
    }

    /// 关联新外部身份仍要求当前账号重新认证，后端执行唯一归属检查。
    public func bindExternal(provider: String, credential: String, reauthentication: AuthReauthentication) async throws {
        guard !isSigningIn else { throw AuthError.superseded }
        let operation = generation
        try await refreshIfNeeded()
        guard operation == generation, !isSigningIn, let current = session else { throw AuthError.superseded }
        try await managementBackend().bindExternal(provider: provider, credential: credential, reauthentication: reauthentication, accessToken: current.accessToken)
        try requireCurrentManagementSession(current, operation: operation)
    }

    /// 至少保留一种可用登录方式的检查归服务端事务负责。
    public func unlinkIdentity(_ identity: AuthLoginIdentity, reauthentication: AuthReauthentication) async throws {
        guard !isSigningIn else { throw AuthError.superseded }
        let operation = generation
        try await refreshIfNeeded()
        guard operation == generation, !isSigningIn, let current = session else { throw AuthError.superseded }
        try await managementBackend().unlinkIdentity(identity, reauthentication: reauthentication, accessToken: current.accessToken)
        try requireCurrentManagementSession(current, operation: operation)
    }

    /// generation 不覆盖同账号内 refresh；返回前同时确认账号及实际会话仍为请求快照。
    private func requireCurrentManagementSession(_ current: AuthSession, operation: Int) throws {
        guard !isSigningIn, operation == generation, let active = session,
              active.user.id == current.user.id, active.accessToken == current.accessToken
        else { throw AuthError.superseded }
    }

    private func managementBackend() throws -> any AccountManagementAuthBackend {
        guard let result = backend as? any AccountManagementAuthBackend else { throw AuthError.invalidConfiguration }
        return result
    }

    /// 后端重置成功后清理已撤销的本地凭据；迟到响应不能清掉后续新登录。
    public func resetPassword(email: String, password: String, code: String, challengeID: String) async throws {
        let operation = generation
        try await emailBackend().resetPassword(email: email, password: password, code: code, challengeID: challengeID)
        guard operation == generation else { return }
        generation += 1
        refreshTask = nil
        isSigningIn = false
        session = nil
        provider?.signOut()
        // 重置已在服务端撤销旧会话，不能再携带已撤销 access 调用 logout。
        try tokenStore.delete()
    }

    /// 页面取消时失效在途登录，但保留已经安装的会话；迟到凭据仍会被撤销。
    public func cancelPendingAuthentication() {
        guard isSigningIn else { return }
        generation += 1
        refreshTask = nil
        isSigningIn = false
    }

    private func emailBackend() throws -> any EmailPasswordAuthBackend {
        guard let emailBackend = backend as? any EmailPasswordAuthBackend else { throw AuthError.invalidConfiguration }
        return emailBackend
    }

    /// 冷启动只使用应用 refresh token，不恢复 Google profile 充当已登录状态。
    public func restore() async throws {
        guard try tokenStore.load() != nil else { return }
        try await refresh()
    }

    /// 业务请求前保留至少 60 秒 access 有效期；冷启动允许仅用 Keychain 恢复。
    public func refreshIfNeeded() async throws {
        if let session, session.expiresAt.timeIntervalSince(now()) >= 60 { return }
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
                provider?.signOut()
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
        provider?.signOut()
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
        if Task.isCancelled { try await reject(response, error: CancellationError()) }
        do { try tokenStore.save(response.refreshToken) }
        catch {
            session = nil
            try await reject(response, error: error)
        }
        session = AuthSession(accessToken: response.accessToken, expiresAt: now().addingTimeInterval(response.expiresIn), user: response.user)
    }

    /// 已收到新凭据但不能安装时撤销新 access；不取消在途刷新而丢失撤销凭据。
    private func reject(_ response: AuthTokenResponse, error operationError: any Error) async throws -> Never {
        // 清理任务不继承调用方取消，否则 URLSession 会立即取消撤销请求。
        let revocation = Task { @MainActor in try await backend.logout(accessToken: response.accessToken) }
        do { try await revocation.value }
        catch { throw AuthCleanupError(operationError: operationError, revocationError: error) }
        throw operationError
    }
}
