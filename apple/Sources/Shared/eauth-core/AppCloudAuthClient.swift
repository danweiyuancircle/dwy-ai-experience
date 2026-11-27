import Foundation

/// 应用后端认证 HTTP 客户端；保留宿主 baseURL 中的完整应用前缀。
@MainActor
public final class AppCloudAuthClient: EmailPasswordAuthBackend, AppleAuthBackend, AppleReauthenticationBackend, AccountManagementAuthBackend, ExternalAuthBackend {
    public let baseURL: URL
    private let session: URLSession
    /// 每次请求读取当前首选语言；宿主可注入应用内语言，默认跟随设备系统。
    private let languageProvider: @MainActor @Sendable () -> String?
    /// 业务方每次会话交换重新读取准入证明；默认 nil 保持通用项目行为。
    private let admissionProofProvider: (@MainActor @Sendable () async throws -> String)?

    /// 生产只接受 HTTPS；本机开发允许明确的 loopback HTTP。
    /// languageProvider 返回语言标签（如 zh-Hans、en-US），中文以外统一请求英文。
    public init(baseURL: URL, session: URLSession = .shared, languageProvider: @escaping @MainActor @Sendable () -> String? = { Locale.preferredLanguages.first }, admissionProofProvider: (@MainActor @Sendable () async throws -> String)? = nil) throws {
        guard baseURL.host != nil, baseURL.user == nil, baseURL.password == nil,
              baseURL.query == nil, baseURL.fragment == nil,
              baseURL.scheme == "https" || (baseURL.scheme == "http" && ["localhost", "127.0.0.1", "::1"].contains(baseURL.host))
        else { throw AuthError.invalidConfiguration }
        self.baseURL = baseURL
        self.session = session
        self.languageProvider = languageProvider
        self.admissionProofProvider = admissionProofProvider
    }

    /// ID token 仅用于本次后端交换，设备 UUID 不参与认证证明。
    public func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse {
        guard !googleIDToken.isEmpty, googleIDToken.utf8.count <= 16_384 else { throw AuthError.invalidResponse }
        let body = GoogleBody(idToken: googleIDToken, deviceID: deviceID)
        return try await sessionExchange(path: "google", body: body)
    }

    /// 外部凭据为 provider 定义的有界字符串；身份真伪与准入都由后端验证。
    public func authenticate(provider: String, credential: String, deviceID: UUID) async throws -> AuthTokenResponse {
        guard !provider.isEmpty, provider.utf8.count <= 64, !credential.isEmpty, credential.utf8.count <= 16_384 else { throw AuthError.invalidResponse }
        return try await sessionExchange(path: "external/login", body: ExternalLoginBody(provider: provider, credential: credential, deviceID: deviceID))
    }

    /// 挑战属于 baseURL 对应应用；nonce 只用于本次系统授权。
    public func createAppleChallenge() async throws -> AppleSignInChallenge {
        let data = try await request(path: "apple/challenges", body: nil, accessToken: nil)
        return try decodeAppleChallenge(data)
    }

    /// 管理挑战必须使用当前会话，服务端将主体和用途写入同一挑战记录。
    public func createAppleChallenge(purpose: AppleReauthenticationPurpose, accessToken: String) async throws -> AppleSignInChallenge {
        try validateAccessToken(accessToken)
        let body = try JSONEncoder().encode(["purpose": purpose.rawValue])
        let data = try await request(path: "apple/challenges", body: body, accessToken: accessToken)
        return try decodeAppleChallenge(data)
    }

    private func decodeAppleChallenge(_ data: Data) throws -> AppleSignInChallenge {
        let envelope: AppleChallengeEnvelope = try decode(data)
        guard let challenge = envelope.data,
              !challenge.challengeId.isEmpty, challenge.challengeId.utf8.count <= 4_096,
              !challenge.nonce.isEmpty, challenge.nonce.utf8.count <= 4_096,
              challenge.expiresIn.isFinite, challenge.expiresIn > 0
        else { throw AuthError.invalidResponse }
        return AppleSignInChallenge(challengeID: challenge.challengeId, nonce: challenge.nonce, expiresIn: challenge.expiresIn)
    }

    /// Apple 短时凭据只交换自家会话；服务端验证身份、挑战与应用受众。
    public func authenticate(appleAuthorization: AppleAuthorization, challengeID: String, deviceID: UUID) async throws -> AuthTokenResponse {
        guard !challengeID.isEmpty, challengeID.utf8.count <= 4_096,
              !appleAuthorization.identityToken.isEmpty, appleAuthorization.identityToken.utf8.count <= 16_384,
              !appleAuthorization.authorizationCode.isEmpty, appleAuthorization.authorizationCode.utf8.count <= 4_096,
              (appleAuthorization.displayName?.unicodeScalars.count ?? 0) <= 255
        else { throw AuthError.invalidResponse }
        let body = AppleBody(challengeID: challengeID, identityToken: appleAuthorization.identityToken, authorizationCode: appleAuthorization.authorizationCode, deviceID: deviceID, displayName: appleAuthorization.displayName)
        return try await sessionExchange(path: "apple", body: body)
    }

    /// 发码只传邮箱与用途，密码不会进入邮件请求。
    public func sendEmailCode(email: String, purpose: EmailCodePurpose) async throws -> EmailCodeChallenge {
        guard EmailPasswordRules.isValidEmail(email) else { throw AuthError.invalidResponse }
        let body = EmailCodeBody(email: EmailPasswordRules.normalizedEmail(email), purpose: purpose)
        let data = try await request(path: "email/code", body: JSONEncoder().encode(body), accessToken: nil)
        return try challenge(data)
    }

    /// Bearer 与重新认证共同约束邮箱变更，不使用公开注册验证码路径。
    public func sendEmailUpdateCode(email: String, reauthentication: AuthReauthentication, accessToken: String) async throws -> EmailCodeChallenge {
        try validateAccessToken(accessToken)
        guard EmailPasswordRules.isValidEmail(email), EmailPasswordRules.normalizedEmail(email).unicodeScalars.count <= 254 else { throw AuthError.invalidResponse }
        let data = try await request(path: "email/update/code", body: JSONEncoder().encode(EmailUpdateCodeBody(email: EmailPasswordRules.normalizedEmail(email), reauthentication: reauthentication)), accessToken: accessToken)
        return try challenge(data)
    }

    /// 新密码省略时保留现密码；首次建立邮箱密码的约束由服务端执行。
    public func updateEmail(email: String, code: String, challengeID: String, newPassword: String?, accessToken: String) async throws -> AuthTokenResponse {
        try validateAccessToken(accessToken)
        guard EmailPasswordRules.isValidEmail(email), EmailPasswordRules.normalizedEmail(email).unicodeScalars.count <= 254,
              code.utf8.count == 6, code.utf8.allSatisfy({ (48...57).contains($0) }), challengeID.utf8.count == 36, UUID(uuidString: challengeID) != nil,
              newPassword.map(EmailPasswordRules.isValidNewPassword) ?? true
        else { throw AuthError.invalidResponse }
        return try await sessionExchange(path: "email/update", body: EmailUpdateBody(email: EmailPasswordRules.normalizedEmail(email), code: code, challengeID: challengeID, newPassword: newPassword), accessToken: accessToken)
    }

    /// 只读取当前主体的入口，服务端不接受目标 subject。
    public func listIdentities(accessToken: String) async throws -> [AuthLoginIdentity] {
        try validateAccessToken(accessToken)
        let data = try await request(path: "identities", body: nil, accessToken: accessToken, method: "GET")
        let envelope: IdentityEnvelope = try decode(data)
        guard let identities = envelope.data, identities.count <= 64,
              identities.allSatisfy({ !$0.value.isEmpty && $0.value.unicodeScalars.count <= 255 && ($0.provider?.utf8.count ?? 0) <= 64 && ($0.issuer?.utf8.count ?? 0) <= 512 })
        else { throw AuthError.invalidResponse }
        return identities
    }

    /// 新外部凭据与当前账号证明分开提交，不按相同邮箱合并账户。
    public func bindExternal(provider: String, credential: String, reauthentication: AuthReauthentication, accessToken: String) async throws {
        try validateAccessToken(accessToken)
        guard !provider.isEmpty, provider.utf8.count <= 64, !credential.isEmpty, credential.utf8.count <= 16_384 else { throw AuthError.invalidResponse }
        try await completed(path: "external/bind", body: JSONEncoder().encode(ExternalBindingBody(provider: provider, credential: credential, reauthentication: reauthentication)), accessToken: accessToken)
    }

    /// 最后入口保护由服务端事务执行；客户端只提交列表返回的精确定位。
    public func unlinkIdentity(_ identity: AuthLoginIdentity, reauthentication: AuthReauthentication, accessToken: String) async throws {
        try validateAccessToken(accessToken)
        guard !identity.value.isEmpty, identity.value.unicodeScalars.count <= 255,
              (identity.provider?.utf8.count ?? 0) <= 64, (identity.issuer?.utf8.count ?? 0) <= 512
        else { throw AuthError.invalidResponse }
        try await completed(path: "identity/unlink", body: JSONEncoder().encode(UnlinkBody(kind: identity.kind, value: identity.value, provider: identity.provider, issuer: identity.issuer, reauthentication: reauthentication)), accessToken: accessToken)
    }

    private func completed(path: String, body: Data, accessToken: String) async throws {
        let data = try await request(path: path, body: body, accessToken: accessToken)
        let envelope: ResetEnvelope = try decode(data)
        guard envelope.data?.status == "completed" else { throw AuthError.invalidResponse }
    }

    private func validateAccessToken(_ accessToken: String) throws {
        guard !accessToken.isEmpty, accessToken.utf8.count <= 4_096,
              !accessToken.contains(where: { $0.isWhitespace || $0.isNewline })
        else { throw AuthError.invalidResponse }
    }

    private func challenge(_ data: Data) throws -> EmailCodeChallenge {
        let envelope: ChallengeEnvelope = try decode(data)
        guard let result = envelope.data, !result.challengeId.isEmpty, result.challengeId.utf8.count <= 4_096,
              result.expiresIn.isFinite, result.expiresIn > 0, result.resendAfter.isFinite, result.resendAfter >= 0,
              (1...32).contains(result.codeLength)
        else { throw AuthError.invalidResponse }
        return EmailCodeChallenge(challengeID: result.challengeId, expiresIn: result.expiresIn, resendAfter: result.resendAfter, codeLength: result.codeLength)
    }

    /// 登录只检查非空与字节上限，历史账号不受新密码最低长度约束。
    public func authenticate(email: String, password: String, deviceID: UUID) async throws -> AuthTokenResponse {
        guard EmailPasswordRules.isValidEmail(email), EmailPasswordRules.isValidLoginPassword(password) else { throw AuthError.invalidResponse }
        return try await sessionExchange(path: "login", body: EmailCredentialsBody(email: EmailPasswordRules.normalizedEmail(email), password: password, deviceID: deviceID))
    }

    /// 注册要求当前密码政策；设备标识只用于会话管理。
    public func register(email: String, password: String, code: String, challengeID: String, deviceID: UUID) async throws -> AuthTokenResponse {
        try validateNewCredentials(email: email, password: password, code: code, challengeID: challengeID)
        let body = EmailVerificationBody(email: EmailPasswordRules.normalizedEmail(email), password: password, code: code, challengeID: challengeID, deviceID: deviceID)
        return try await sessionExchange(path: "register", body: body)
    }

    /// 重置成功必须返回 completed，成功信封本身不能证明密码已经更新。
    public func resetPassword(email: String, password: String, code: String, challengeID: String) async throws {
        try validateNewCredentials(email: email, password: password, code: code, challengeID: challengeID)
        let body = EmailVerificationBody(email: EmailPasswordRules.normalizedEmail(email), password: password, code: code, challengeID: challengeID, deviceID: nil)
        let data = try await request(path: "password/reset", body: JSONEncoder().encode(body), accessToken: nil)
        let envelope: ResetEnvelope = try decode(data)
        guard envelope.data?.status == "completed" else { throw AuthError.invalidResponse }
    }

    private func validateNewCredentials(email: String, password: String, code: String, challengeID: String) throws {
        guard EmailPasswordRules.isValidEmail(email), EmailPasswordRules.isValidNewPassword(password),
              code.utf8.count == 6, code.utf8.allSatisfy({ (48...57).contains($0) }),
              !challengeID.isEmpty, challengeID.utf8.count <= 4_096
        else { throw AuthError.invalidResponse }
    }

    private func decode<T: Decodable>(_ data: Data) throws -> T {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        do { return try decoder.decode(T.self, from: data) }
        catch is DecodingError { throw AuthError.invalidResponse }
    }

    /// 后端轮换 refresh token；调用方必须保存返回的新 token。
    public func refresh(refreshToken: String) async throws -> AuthTokenResponse {
        guard !refreshToken.isEmpty, refreshToken.utf8.count <= 4_096 else { throw AuthError.invalidResponse }
        return try await sessionExchange(path: "refresh", body: RefreshBody(refreshToken: refreshToken))
    }

    /// 只在创建/恢复会话入口附带业务证明，验证码及密码重置仍可独立使用。
    private func sessionExchange<Body: Encodable>(path: String, body: Body, accessToken: String? = nil) async throws -> AuthTokenResponse {
        let proof = try await admissionProofProvider?()
        if let proof {
            guard !proof.isEmpty, proof.utf8.count <= 131_072 else { throw AuthError.invalidResponse }
        }
        return try await exchange(path: path, body: JSONEncoder().encode(AdmissionBody(payload: body, proof: proof)), accessToken: accessToken)
    }

    /// 后端撤销当前会话；本地清理由 AuthSessionStore 先行完成。
    public func logout(accessToken: String) async throws {
        guard !accessToken.isEmpty, accessToken.utf8.count <= 4_096,
              !accessToken.contains(where: { $0.isWhitespace || $0.isNewline })
        else { throw AuthError.invalidResponse }
        _ = try await request(path: "logout", body: nil, accessToken: accessToken)
    }

    /// 键名只在 HTTP 边界转换，业务模型使用 Swift 风格。
    private func exchange(path: String, body: Data, accessToken: String? = nil) async throws -> AuthTokenResponse {
        let data = try await request(path: path, body: body, accessToken: accessToken)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        let envelope: TokenEnvelope
        do { envelope = try decoder.decode(TokenEnvelope.self, from: data) }
        catch is DecodingError { throw AuthError.invalidResponse }
        guard let tokens = envelope.data, tokens.tokenType == "Bearer",
              !tokens.accessToken.isEmpty, tokens.accessToken.utf8.count <= 4_096,
              !tokens.refreshToken.isEmpty, tokens.refreshToken.utf8.count <= 4_096,
              tokens.expiresIn.isFinite, tokens.expiresIn > 0,
              (tokens.user.email?.count ?? 0) <= 320,
              (tokens.user.displayName?.count ?? 0) <= 255
        else { throw AuthError.invalidResponse }
        return AuthTokenResponse(accessToken: tokens.accessToken, refreshToken: tokens.refreshToken, expiresIn: tokens.expiresIn, user: tokens.user)
    }

    /// 先验证状态与 eapi 信封；错误 message 不直接展示，避免后端内部细节进入 UI。
    private func request(path: String, body: Data?, accessToken: String?, method: String = "POST") async throws -> Data {
        let url = baseURL.appendingPathComponent("api/v1/auth").appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.timeoutInterval = 30
        request.httpBody = body
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        let preferredLanguage = languageProvider()?.lowercased()
        let language = preferredLanguage == "zh" || preferredLanguage?.hasPrefix("zh-") == true ? "zh" : "en"
        request.setValue(language, forHTTPHeaderField: "Accept-Language")
        if body != nil { request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        if let accessToken { request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization") }
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse, data.count <= 65_536 else { throw AuthError.invalidResponse }
        let envelope: StatusEnvelope
        do { envelope = try JSONDecoder().decode(StatusEnvelope.self, from: data) }
        catch is DecodingError { throw AuthError.invalidResponse }
        guard (200..<300).contains(http.statusCode), envelope.code == "SUCCESS" else {
            throw AuthError.server(code: envelope.code, message: String(envelope.message.prefix(500)))
        }
        return data
    }
}
/// 同一强类型请求只追加准入字段，不经松散字典重写凭据或破坏旧接口。
private struct AdmissionBody<Payload: Encodable>: Encodable {
    let payload: Payload
    let proof: String?
    private enum CodingKeys: String, CodingKey { case proof = "admission_proof" }
    func encode(to encoder: any Encoder) throws {
        try payload.encode(to: encoder)
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encodeIfPresent(proof, forKey: .proof)
    }
}

private struct ExternalLoginBody: Encodable {
    let provider: String
    let credential: String
    let deviceID: UUID
    enum CodingKeys: String, CodingKey { case provider, credential, deviceID = "device_id" }
}

private struct AppleBody: Encodable {
    let challengeID: String
    let identityToken: String
    let authorizationCode: String
    let deviceID: UUID
    let displayName: String?
    enum CodingKeys: String, CodingKey {
        case challengeID = "challenge_id", identityToken = "identity_token", authorizationCode = "authorization_code"
        case deviceID = "device_id", displayName = "display_name"
    }
}
private struct AppleChallengeEnvelope: Decodable {
    let data: AppleChallengeData?
}
private struct AppleChallengeData: Decodable {
    let challengeId: String
    let nonce: String
    let expiresIn: TimeInterval
}

private struct EmailCodeBody: Encodable {
    let email: String
    let purpose: EmailCodePurpose
}
private struct EmailCredentialsBody: Encodable {
    let email: String
    let password: String
    let deviceID: UUID
    enum CodingKeys: String, CodingKey { case email, password, deviceID = "device_id" }
}
private struct EmailVerificationBody: Encodable {
    let email: String
    let password: String
    let code: String
    let challengeID: String
    let deviceID: UUID?
    enum CodingKeys: String, CodingKey { case email, password, code, challengeID = "challenge_id", deviceID = "device_id" }
}
private struct ChallengeEnvelope: Decodable {
    let data: ChallengeData?
}
private struct ChallengeData: Decodable {
    let challengeId: String
    let expiresIn: TimeInterval
    let resendAfter: TimeInterval
    let codeLength: Int
}
private struct ResetEnvelope: Decodable {
    let data: ResetData?
}
private struct ResetData: Decodable {
    let status: String
}

/// 固定 schema 避免松散字典把不受支持字段传到认证服务。
private struct GoogleBody: Encodable {
    let idToken: String
    let deviceID: UUID
    enum CodingKeys: String, CodingKey { case idToken = "id_token", deviceID = "device_id" }
}
private struct RefreshBody: Encodable {
    let refreshToken: String
    enum CodingKeys: String, CodingKey { case refreshToken = "refresh_token" }
}
/// eapi 状态先于业务 payload 验证，错误信封无需伪造 token data。
private struct StatusEnvelope: Decodable {
    let code: String
    let message: String
}
/// 仅解交换 payload，timestamp 由服务端使用且不参与客户端有效期判断。
private struct TokenEnvelope: Decodable {
    let data: TokenData?
}
/// 后端 token schema 的内部表示，不泄露 snake_case 到公共 API。
private struct TokenData: Decodable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let expiresIn: TimeInterval
    let user: AuthUser
}


/// 账号管理请求固定 schema，不接收 owner/device/任意 profile 字典。
private struct EmailUpdateCodeBody: Encodable {
    let email: String
    let reauthentication: AuthReauthentication
}
private struct EmailUpdateBody: Encodable {
    let email: String
    let code: String
    let challengeID: String
    let newPassword: String?
    enum CodingKeys: String, CodingKey { case email, code, challengeID = "challenge_id", newPassword = "new_password" }
}
private struct ExternalBindingBody: Encodable {
    let provider: String
    let credential: String
    let reauthentication: AuthReauthentication
}
private struct UnlinkBody: Encodable {
    let kind: AuthLoginIdentity.Kind
    let value: String
    let provider: String?
    let issuer: String?
    let reauthentication: AuthReauthentication
}
private struct IdentityEnvelope: Decodable {
    let data: [AuthLoginIdentity]?
}
