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

/// 宿主选择原生授权适配器；取消抛 CancellationError，不把 Apple token 持久化。
@MainActor
public protocol AppleAuthorizationProviding {
    func signIn(nonce: String) async throws -> AppleAuthorization
}
