#if os(macOS)
import AppKit
import AuthCore
import GoogleSignIn

/// 公开 OAuth 标识；serverClientID 必须是应用后端验证的 audience，不包含客户端密钥。
public struct MacGoogleSignInConfiguration: Sendable {
    public let clientID: String
    public let serverClientID: String

    /// 标识缺失或不属于 Google OAuth 客户端命名空间时拒绝配置。
    public init(clientID: String, serverClientID: String) throws {
        guard [clientID, serverClientID].allSatisfy({
            !$0.isEmpty && $0.utf8.count <= 512 && $0.hasSuffix(".apps.googleusercontent.com")
                && !$0.contains(where: { $0.isWhitespace })
        }) else { throw AuthError.invalidConfiguration }
        self.clientID = clientID
        self.serverClientID = serverClientID
    }

    /// 宿主在 CFBundleURLSchemes 注册此 scheme，并将对应回调交给 provider。
    public var reversedURLScheme: String { clientID.split(separator: ".").reversed().joined(separator: ".") }
}

/// Google 官方 SDK 的 macOS 呈现适配；只返回 ID token，可信账号以应用后端交换结果为准。
@MainActor
public final class MacGoogleSignInProvider: GoogleIDTokenProviding {
    private let configuration: MacGoogleSignInConfiguration
    private let presentingWindow: () -> NSWindow?

    /// 仅由用户主动登录时调用；窗口由宿主提供，不能在冷启动时自动打开认证浏览器。
    public init(configuration: MacGoogleSignInConfiguration, presentingWindow: @escaping () -> NSWindow?) {
        self.configuration = configuration
        self.presentingWindow = presentingWindow
    }

    /// 用户主动触发且存在呈现窗口时才打开官方登录流程；取消与 SDK 错误原样抛回宿主。
    public func signIn() async throws -> String {
        guard let window = presentingWindow() else { throw AuthError.invalidConfiguration }
        GIDSignIn.sharedInstance.configuration = GIDConfiguration(clientID: configuration.clientID, serverClientID: configuration.serverClientID)
        return try await withCheckedThrowingContinuation { continuation in
            GIDSignIn.sharedInstance.signIn(withPresenting: window) { result, error in
                if let error { continuation.resume(throwing: error) }
                else if let token = result?.user.idToken?.tokenString, !token.isEmpty { continuation.resume(returning: token) }
                else { continuation.resume(throwing: AuthError.invalidResponse) }
            }
        }
    }

    /// 只清理本 SDK 的登录状态，不撤销用户在其他 Google 应用中的授权。
    public func signOut() { GIDSignIn.sharedInstance.signOut() }

    /// 无关 scheme 返回 false，由宿主继续处理自己的 deep link。
    @discardableResult
    public func handleURL(_ url: URL) -> Bool {
        guard url.scheme == configuration.reversedURLScheme else { return false }
        return GIDSignIn.sharedInstance.handle(url)
    }
}
#endif
