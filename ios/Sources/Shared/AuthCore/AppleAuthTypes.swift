import Foundation

/// 服务端一次性挑战；nonce 原样传给 Apple request.nonce，不做 Firebase 哈希转换。
public struct AppleSignInChallenge: Sendable {
    public let challengeID: String
    public let nonce: String
    public let expiresIn: TimeInterval

    public init(challengeID: String, nonce: String, expiresIn: TimeInterval) {
        self.challengeID = challengeID
        self.nonce = nonce
        self.expiresIn = expiresIn
    }
}

/// 系统授权的短时交换材料，只保留在内存；姓名不是身份凭据。
public struct AppleAuthorization: Sendable {
    public let identityToken: String
    public let authorizationCode: String
    public let displayName: String?

    public init(identityToken: String, authorizationCode: String, displayName: String? = nil) {
        self.identityToken = identityToken
        self.authorizationCode = authorizationCode
        self.displayName = displayName
    }
}

/// 可选 Apple 能力，现有 Google/邮箱后端无需实现新增方法。
@MainActor
public protocol AppleAuthBackend: AuthBackend {
    func createAppleChallenge() async throws -> AppleSignInChallenge
    func authenticate(appleAuthorization: AppleAuthorization, challengeID: String, deviceID: UUID) async throws -> AuthTokenResponse
}

/// 服务端挑战绑定当前主体与单次管理操作，不能与登录或其他管理用途互换。
public enum AppleReauthenticationPurpose: String, Sendable {
    case bind = "reauth_bind"
    case unlink = "reauth_unlink"
    case emailUpdate = "reauth_email_update"
}

/// Apple 账号管理的可选能力，现有登录适配器无需增加实现。
@MainActor
public protocol AppleReauthenticationBackend: AuthBackend {
    func createAppleChallenge(purpose: AppleReauthenticationPurpose, accessToken: String) async throws -> AppleSignInChallenge
}

/// 宿主选择原生授权适配器；取消抛 CancellationError，不把 Apple token 持久化。
@MainActor
public protocol AppleAuthorizationProviding {
    func signIn(nonce: String) async throws -> AppleAuthorization
}
