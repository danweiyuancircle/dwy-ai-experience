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
