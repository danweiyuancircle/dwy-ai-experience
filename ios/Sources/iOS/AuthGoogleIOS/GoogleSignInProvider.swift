#if os(iOS)
import Foundation
import UIKit
import GoogleSignIn
import AuthCore

/// 公开 OAuth 标识，不包含 client secret；serverClientID 必须等于后端验证的 web audience。
public struct GoogleSignInConfiguration: Sendable {
    public let iOSClientID: String
    public let serverClientID: String

    public init(iOSClientID: String, serverClientID: String) throws {
        guard [iOSClientID, serverClientID].allSatisfy({ !$0.isEmpty && $0.utf8.count <= 512 && $0.hasSuffix(".apps.googleusercontent.com") }) else {
            throw AuthError.invalidConfiguration
        }
        self.iOSClientID = iOSClientID
        self.serverClientID = serverClientID
    }

    /// 宿主注册为 CFBundleURLSchemes，不由共享库修改 Info.plist。
    public var reversedURLScheme: String { iOSClientID.split(separator: ".").reversed().joined(separator: ".") }
}

/// 官方 GoogleSignIn SDK 的 iOS 呈现适配，不自行实现 OAuth/PKCE，不请求 Gmail 权限。
@MainActor
public final class GoogleSignInProvider: GoogleIDTokenProviding {
    private let configuration: GoogleSignInConfiguration
    private let presentingViewController: () -> UIViewController?

    /// 由宿主提供当前可呈现的控制器，禁止从全局窗口猜测 scene。
    public init(configuration: GoogleSignInConfiguration, presentingViewController: @escaping () -> UIViewController?) {
        self.configuration = configuration
        self.presentingViewController = presentingViewController
    }

    /// SDK 验证 OAuth 回调；库只转交 ID token，账户身份以应用后端为准。
    public func signIn() async throws -> String {
        guard let controller = presentingViewController() else { throw AuthError.invalidConfiguration }
        GIDSignIn.sharedInstance.configuration = GIDConfiguration(clientID: configuration.iOSClientID, serverClientID: configuration.serverClientID)
        // 官方 completion 在主队列执行；仅转交 String，避免旧 Swift 将非 Sendable 的 ObjC 结果跨 actor 传递。
        return try await withCheckedThrowingContinuation { continuation in
            GIDSignIn.sharedInstance.signIn(withPresenting: controller) { result, error in
                if let error {
                    continuation.resume(throwing: error)
                } else if let token = result?.user.idToken?.tokenString, !token.isEmpty {
                    continuation.resume(returning: token)
                } else {
                    continuation.resume(throwing: AuthError.invalidResponse)
                }
            }
        }
    }

    /// 清理 SDK 自有 Google 凭据；不撤销用户对其他 Google 应用的授权。
    public func signOut() { GIDSignIn.sharedInstance.signOut() }

    /// 在宿主 .onOpenURL / AppDelegate 中转交；返回 false 表示不是 Google 回调。
    @discardableResult
    public func handleURL(_ url: URL) -> Bool {
        guard url.scheme == configuration.reversedURLScheme else { return false }
        return GIDSignIn.sharedInstance.handle(url)
    }
}
#endif
