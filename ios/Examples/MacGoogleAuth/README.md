# macOS 可选 Google 账号

宿主链接 `AuthCore`、`AuthGoogleMac`，不在启动时调用交互式 `signIn()`。Google SDK 只提供 ID token，后端交换结果中的用户 UUID 才是应用账号身份。

```swift
import AppKit
import AuthCore
import AuthGoogleMac

/// namespace 使用宿主应用独立标识；window 必须是用户发起登录的窗口。
@MainActor
func makeSession(window: NSWindow, backendURL: URL, namespace: String,
                 clientID: String, serverClientID: String) throws
    -> (AuthSessionStore, MacGoogleSignInProvider) {
    let configuration = try MacGoogleSignInConfiguration(clientID: clientID, serverClientID: serverClientID)
    let provider = MacGoogleSignInProvider(configuration: configuration, presentingWindow: { [weak window] in window })
    let session = AuthSessionStore(
        backend: try AppCloudAuthClient(baseURL: backendURL),
        provider: provider,
        tokenStore: try KeychainRefreshTokenStore(namespace: namespace, backendURL: backendURL),
        deviceID: try AuthDeviceIdentity.loadOrCreate(namespace: namespace))
    return (session, provider)
}
```

公开 OAuth Client ID 来自宿主配置，不包含 client secret。macOS Client ID 对应的反向 scheme 由 `configuration.reversedURLScheme` 提供，宿主注册进 `CFBundleURLTypes`，在 AppDelegate 的 URL 事件中转交 `provider.handleURL(_:)`；回调 URL 不写日志。serverClientID 必须与后端 audience 匹配。

用户点击登录后调用 `try await session.signIn()`；启动恢复使用 `restore()`。网络失败不等于退出，宿主保留账号对应的本地同步库；缓存 userID 只能选择本机数据，不能充当服务端鉴权。切号或退出前先暂停 SyncCoordinator，再切换宿主投影；设备权限、目录书签、令牌不能作为业务同步载荷上传。

同步属性 setter 可使用 `SyncStore.saveLocally(_:using:)`：返回前正文与 outbox 已在同一 SQLite 事务提交，再发布本机投影；禁止通过 semaphore 阻塞等待 actor 或在 schema 校验中访问 UI。远程调用仍交给 SyncCoordinator。

自动化配置用例位于 `ios/Tests/AuthGoogleMacTests/GoogleSignInProviderTests.swift`：拒绝无效 Client ID、忽略无关 URL scheme、没有呈现窗口时禁止发起登录。该用例不代替真实 OAuth 登录和回调验收。
