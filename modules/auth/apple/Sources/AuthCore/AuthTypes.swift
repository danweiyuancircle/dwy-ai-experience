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

/// 主线程隔离统一 SDK、Keychain 和可观察状态，网络等待不阻塞主线程。
@MainActor
public protocol AuthBackend {
    func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse
    func refresh(refreshToken: String) async throws -> AuthTokenResponse
    func logout(accessToken: String) async throws
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
