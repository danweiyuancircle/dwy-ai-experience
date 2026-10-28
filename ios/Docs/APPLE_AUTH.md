# 原生 Apple 登录

SwiftPM 产品：`AuthCore` 与 `AuthAppleIOS`。原生适配最低 iOS 17，不引入第三方 SDK。Apple 能力通过独立 `AppleAuthBackend` 协议声明，现有 `AuthBackend`、Google 与邮箱调用保持兼容。

## 固定版本安装

在宿主 `Package.swift` 使用私有仓库的正式标签，并提交 `Package.resolved`；Xcode 工程也可按相同 URL 和 Exact Version 添加依赖。需要该私有仓库的读取权限，Python 后端包无需仓库权限。

```swift
.package(url: "https://github.com/danweiyuancircle/dwy-ai-experience.git", exact: "0.6.0")
// 宿主 target.dependencies:
.product(name: "AuthCore", package: "dwy-ai-experience"),
.product(name: "AuthAppleIOS", package: "dwy-ai-experience")
```

后端安装和装配见 [Apple 后端接入](../../docs/apple-auth-integration.md)。共享 SDK 不读取某个产品的配置；后端 URL、namespace、当前窗口全部由宿主提供。

## 会话与后端

宿主为每个应用保留独立 Bundle ID、Sign in with Apple capability、签名、后端应用配置和 Keychain namespace。先使用对应应用的完整服务 URL 创建会话：

```swift
import AuthCore
import Foundation

@MainActor
func makeAppleAuthSession(baseURL: URL, namespace: String) throws -> AuthSessionStore {
    let backend = try AppCloudAuthClient(baseURL: baseURL)
    let tokens = try KeychainRefreshTokenStore(namespace: namespace, backendURL: baseURL)
    let deviceID = try AuthDeviceIdentity.loadOrCreate(namespace: namespace)
    return AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: deviceID)
}
```

例如 `baseURL` 为 `https://api.example.com/my-app`，则两次请求分别是：

- `POST https://api.example.com/my-app/api/v1/auth/apple/challenges`，无请求体，返回 `SUCCESS` 信封内的 `challenge_id`、`nonce`、`expires_in`。
- `POST https://api.example.com/my-app/api/v1/auth/apple`，仅发送 `challenge_id`、`identity_token`、`authorization_code`、`device_id` 与可选 `display_name`，返回现有 token/user 信封。

服务端 nonce **原样**赋给 `ASAuthorizationAppleIDRequest.nonce`。不要再次哈希或套用 Firebase nonce 规则。系统首次返回的姓名只是资料，最终用户 UUID、姓名和 email 使用后端响应；库不按邮箱合并身份。

Keychain 只保存本应用 refresh token。Apple identity token 和 authorization code 仅用于本次交换；Apple refresh token、私钥、client_secret 全部留在服务器。

## 官方按钮与宿主锚点

宿主使用官方 `ASAuthorizationAppleIDButton`，点击后由共享适配器统一申请挑战和呈现授权。下面的控制器可直接由宿主呈现，`session` 应与业务请求使用同一个实例。

```swift
import AuthenticationServices
import AuthAppleIOS
import AuthCore
import UIKit

@MainActor
final class AppleLoginViewController: UIViewController {
    private let session: AuthSessionStore
    private let onAuthenticated: (AuthUser) -> Void
    private let onError: (any Error) -> Void
    private var loginTask: Task<Void, Never>?
    private lazy var provider = AppleSignInProvider(presentationAnchor: { [weak self] in
        self?.viewIfLoaded?.window
    })

    init(session: AuthSessionStore, onAuthenticated: @escaping (AuthUser) -> Void, onError: @escaping (any Error) -> Void) {
        self.session = session
        self.onAuthenticated = onAuthenticated
        self.onError = onError
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) { fatalError("Use init(session:onAuthenticated:onError:)") }

    override func viewDidLoad() {
        super.viewDidLoad()
        let button = ASAuthorizationAppleIDButton(type: .signIn, style: .black)
        button.addTarget(self, action: #selector(signIn), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(button)
        NSLayoutConstraint.activate([
            button.centerXAnchor.constraint(equalTo: view.safeAreaLayoutGuide.centerXAnchor),
            button.centerYAnchor.constraint(equalTo: view.safeAreaLayoutGuide.centerYAnchor),
            button.widthAnchor.constraint(equalToConstant: 280),
            button.heightAnchor.constraint(equalToConstant: 50),
        ])
    }

    @objc private func signIn() {
        guard loginTask == nil else { return }
        loginTask = Task { [self] in
            defer { loginTask = nil }
            do {
                try await session.signInWithApple(provider: provider)
                if let user = session.session?.user { onAuthenticated(user) }
            } catch is CancellationError {
                // 系统取消由宿主安静返回页面。
            } catch AuthError.superseded {
                // 退出或关闭页面后旧请求已失效。
            } catch {
                onError(error)
            }
        }
    }

    /// 关闭登录页之前调用；不要因 Apple 系统授权界面的临时呈现而调用。
    func cancelLogin() {
        session.cancelPendingAuthentication()
        loginTask?.cancel()
    }
}
```

SwiftUI 宿主可通过 `UIViewControllerRepresentable` 呈现该控制器，或包装官方 UIKit 按钮。SwiftUI `SignInWithAppleButton` 自身会启动另一套授权流程，不能在它的回调中再启动 `AppleSignInProvider`，否则会重复授权。

锚点必须来自当前宿主窗口；共享库不扫描全局 scene。适配器在一次授权期间保活 controller 和 delegate，拒绝同一 provider 并发呈现，系统或 Task 取消均抛 `CancellationError`。`cancelPendingAuthentication()` 立即使旧代次失效；同时取消宿主 Task 可关闭仍在呈现的 Apple 授权。退出/取消后的迟到后端凭据由共享会话安装路径撤销，不能恢复旧会话。存储失败同样撤销新会话；若撤销也失败，返回 `AuthCleanupError` 保留两份错误。

## 恢复与验收

冷启动显式调用 `session.restore()`；受保护请求前调用 `session.refreshIfNeeded()`；退出调用 `session.signOut()`。这些操作仅管理应用后端会话。宿主仍应监听 Apple credential revoked 通知，按产品需要检查 credential state，并配合后端通知处理；本模块不提供绑定/解绑界面或全局设备退出。

在仓库根执行：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test --disable-automatic-resolution
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild -scheme AppleAppKit-Package -destination 'platform=iOS Simulator,name=iPhone 18 Pro' -clonedSourcePackagesDirPath .build -disableAutomaticPackageResolution -only-testing:AuthAppleIOSTests test CODE_SIGNING_ALLOWED=NO
```

原生适配测试隔离系统 UI，只验证请求、取消与回调生命周期。首次姓名/隐藏邮箱/再次授权、Apple Developer capability 和签名、真实 Apple ID、真机与线上服务端交换需另外验收。源码与 simulator 通过不代表任何产品工程已经接入或发布。
