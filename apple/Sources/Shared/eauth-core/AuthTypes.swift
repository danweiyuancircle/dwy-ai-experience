import Foundation
import CoreKit
import L10nKit

/// 唯一可信身份来自应用后端；不消费 SDK 的 profile 作为授权依据。
public struct AuthUser: Codable, Equatable, Sendable {
    public let id: UUID
    public let email: String?
    public let displayName: String?

    public init(id: UUID, email: String?, displayName: String?) {
        self.id = id
        self.email = email
        self.displayName = displayName
    }
}

/// 后端令牌交换结果；refreshToken 只交给会话存储，禁止日志输出。
public struct AuthTokenResponse: Sendable {
    public let accessToken: String
    public let refreshToken: String
    public let expiresIn: TimeInterval
    public let user: AuthUser

    public init(accessToken: String, refreshToken: String, expiresIn: TimeInterval, user: AuthUser) {
        self.accessToken = accessToken
        self.refreshToken = refreshToken
        self.expiresIn = expiresIn
        self.user = user
    }
}

/// 可观察会话仅包含内存 access token，不暴露持久化 refresh token。
public struct AuthSession: Sendable {
    public let accessToken: String
    public let expiresAt: Date
    public let user: AuthUser
}

/// 认证系统外边界错误；宿主 xcstrings 提供 auth_err_* 中英文文案。
public enum AuthError: UserFacingError, Sendable {
    case invalidConfiguration
    case invalidResponse
    case signedOut
    case superseded
    case keychain(Int32)
    case server(code: String, message: String)

    public var errorDescription: String? {
        switch self {
        case .invalidConfiguration: loc("auth_err_configuration")
        case .invalidResponse: loc("auth_err_response")
        case .signedOut: loc("auth_err_signed_out")
        case .superseded: loc("auth_err_superseded")
        case .keychain: loc("auth_err_storage")
        case .server: loc("auth_err_server")
        }
    }
}

/// 保留本地状态失败及服务端撤销失败，避免清理过程掩盖其中任一错误。
public struct AuthCleanupError: UserFacingError {
    public let operationError: any Error
    public let revocationError: any Error
    public var errorDescription: String? { operationError.localizedDescription }
}

/// 后端已注册成功，但本地会话安装失败；宿主应引导登录，不能重试注册验证码。
public struct AuthRegistrationError: UserFacingError {
    public let installationError: any Error

    /// 原始安装错误可能包含存储与凭据撤销的复合错误，调用方可继续检查。
    public init(installationError: any Error) {
        self.installationError = installationError
    }

    public var errorDescription: String? { installationError.localizedDescription }
}

/// 主线程隔离统一 SDK、Keychain 和可观察状态，网络等待不阻塞主线程。
@MainActor
public protocol AuthBackend {
    func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse
    func refresh(refreshToken: String) async throws -> AuthTokenResponse
    func logout(accessToken: String) async throws
}

/// 可选第三方认证能力；旧 Google-only 适配器无需增加无意义实现。
@MainActor
public protocol ExternalAuthBackend: AuthBackend {
    func authenticate(provider: String, credential: String, deviceID: UUID) async throws -> AuthTokenResponse
}

/// 验证码用途由服务端隔离；注册验证码不能用于重置密码。
public enum EmailCodePurpose: String, Codable, Sendable {
    case register
    case passwordReset = "password_reset"
}

/// 服务端发码结果；倒计时与输入长度使用服务端返回值。
public struct EmailCodeChallenge: Sendable {
    public let challengeID: String
    public let expiresIn: TimeInterval
    public let resendAfter: TimeInterval
    public let codeLength: Int

    public init(challengeID: String, expiresIn: TimeInterval, resendAfter: TimeInterval, codeLength: Int) {
        self.challengeID = challengeID
        self.expiresIn = expiresIn
        self.resendAfter = resendAfter
        self.codeLength = codeLength
    }
}

/// 邮箱能力单独声明，现有 Google-only 后端不需要实现新增方法。
@MainActor
public protocol EmailPasswordAuthBackend: AuthBackend {
    func sendEmailCode(email: String, purpose: EmailCodePurpose) async throws -> EmailCodeChallenge
    func authenticate(email: String, password: String, deviceID: UUID) async throws -> AuthTokenResponse
    func register(email: String, password: String, code: String, challengeID: String, deviceID: UUID) async throws -> AuthTokenResponse
    func resetPassword(email: String, password: String, code: String, challengeID: String) async throws
}

/// UI 与 HTTP 共用输入政策；密码原样发送，bcrypt 的 UTF-8 上限不能靠截断绕过。
public enum EmailPasswordRules {
    public static let minimumPasswordLength = 15
    public static let maximumPasswordBytes = 72

    public static func normalizedEmail(_ email: String) -> String {
        email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
    }

    /// 仅做本地结构预检；邮箱有效性与投递能力仍由后端验证。
    public static func isValidEmail(_ email: String) -> Bool {
        let normalized = normalizedEmail(email)
        let parts = normalized.split(separator: "@", omittingEmptySubsequences: false)
        return normalized.unicodeScalars.count <= 320 && parts.count == 2 && !parts[0].isEmpty && !parts[1].isEmpty
            && !normalized.contains(where: { $0.isWhitespace || $0.isNewline })
    }

    public static func isValidLoginPassword(_ password: String) -> Bool {
        !password.isEmpty && password.utf8.count <= maximumPasswordBytes
    }

    public static func isValidNewPassword(_ password: String) -> Bool {
        // Python 后端按 Unicode code point 计数，不能使用 Swift 的扩展字素簇数量。
        password.unicodeScalars.count >= minimumPasswordLength && password.utf8.count <= maximumPasswordBytes
    }
}

/// SDK 适配只返回一次性 ID token；Google OAuth 与凭证管理交官方 SDK。
@MainActor
public protocol GoogleIDTokenProviding {
    func signIn() async throws -> String
    func signOut()
}

/// 单活动账号槽位；每个应用与后端使用独立命名空间。
@MainActor
public protocol RefreshTokenStoring {
    func load() throws -> String?
    func save(_ token: String) throws
    func delete() throws
}


/// 重新认证仅携带当前登录方式的证明，不能声明账号 subject 或复用登录结果。
public enum AuthReauthentication: Encodable, Sendable {
    case email(identifier: String, password: String)
    case username(identifier: String, password: String)
    case external(provider: String, credential: String)
    case apple(authorization: AppleAuthorization, challengeID: String)

    private enum CodingKeys: String, CodingKey { case method, identifier, password, credential }

    public func encode(to encoder: any Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        switch self {
        case let .apple(authorization, challengeID):
            guard !challengeID.isEmpty, challengeID.utf8.count <= 36,
                  !authorization.identityToken.isEmpty, authorization.identityToken.utf8.count <= 16_384,
                  !authorization.authorizationCode.isEmpty, authorization.authorizationCode.utf8.count <= 4_096
            else { throw AuthError.invalidResponse }
            let data = try JSONEncoder().encode([
                "challenge_id": challengeID,
                "identity_token": authorization.identityToken,
                "authorization_code": authorization.authorizationCode,
            ])
            guard data.count <= 32_768 else { throw AuthError.invalidResponse }
            try container.encode("external", forKey: .method)
            try container.encode("apple", forKey: .identifier)
            try container.encode(String(decoding: data, as: UTF8.self), forKey: .credential)
        case let .email(identifier, password), let .username(identifier, password):
            let method: String
            if case .email = self { method = "email" } else { method = "username" }
            guard !identifier.isEmpty, identifier.unicodeScalars.count <= (method == "email" ? 254 : 64),
                  EmailPasswordRules.isValidLoginPassword(password)
            else { throw AuthError.invalidResponse }
            try container.encode(method, forKey: .method)
            try container.encode(identifier, forKey: .identifier)
            try container.encode(password, forKey: .password)
        case let .external(provider, credential):
            guard !provider.isEmpty, provider.utf8.count <= 64,
                  !credential.isEmpty, credential.utf8.count <= 16_384
            else { throw AuthError.invalidResponse }
            try container.encode("external", forKey: .method)
            try container.encode(provider, forKey: .identifier)
            try container.encode(credential, forKey: .credential)
        }
    }
}

/// 当前主体可用的入口；外部身份使用 provider/issuer/value 精确定位解绑目标。
public struct AuthLoginIdentity: Codable, Equatable, Sendable {
    public enum Kind: String, Codable, Sendable { case email, username, external }
    public let kind: Kind
    public let value: String
    public let provider: String?
    public let issuer: String?

    public init(kind: Kind, value: String, provider: String? = nil, issuer: String? = nil) {
        self.kind = kind
        self.value = value
        self.provider = provider
        self.issuer = issuer
    }
}

/// 账号管理独立于基础登录协议，旧宿主无需实现；每次敏感调用由当前会话授权。
@MainActor
public protocol AccountManagementAuthBackend: AuthBackend {
    func listIdentities(accessToken: String) async throws -> [AuthLoginIdentity]
    func sendEmailUpdateCode(email: String, reauthentication: AuthReauthentication, accessToken: String) async throws -> EmailCodeChallenge
    func updateEmail(email: String, code: String, challengeID: String, newPassword: String?, accessToken: String) async throws -> AuthTokenResponse
    func bindExternal(provider: String, credential: String, reauthentication: AuthReauthentication, accessToken: String) async throws
    func unlinkIdentity(_ identity: AuthLoginIdentity, reauthentication: AuthReauthentication, accessToken: String) async throws
}
