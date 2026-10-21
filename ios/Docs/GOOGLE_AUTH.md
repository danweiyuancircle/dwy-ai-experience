# Google 登录与 AppCloud 会话

本模块只封装 Google 登录，不读取 Gmail 邮件、不包含邮箱密码登录，也不引入 Firebase Auth。ADBox、RightFlow 尚未接入，已有应用的远程 AppleAppKit 版本引用保持不动。

## 模块与信任边界

- `AuthCore`：后端 HTTP、可信用户、内存 access token、Keychain refresh token、设备 UUID、会话状态机。支持 iOS 17 / macOS 14，不依赖 UIKit 或 Google SDK。
- `AuthGoogleIOS`：官方 GoogleSignIn-iOS 9.1.0 的 iOS 呈现与 URL 回调适配。macOS 不提供此适配类型。
- 宿主 App：AppConfig、登录按钮与页面、当前 scene 的 presenting UIViewController、Info.plist URL scheme、账户路由、错误提示与本地化。
- 后端：验证 Google ID token 的签名、issuer、audience、有效期，建立应用账户，签发并撤销 opaque 应用令牌。客户端不从 SDK profile 判断授权或用户身份。

## 公开配置与初始化

Google Cloud 中为每个 iOS bundle ID 建立 iOS OAuth client；另建 web OAuth client，ID 与后端配置一致。两者的 client ID 都是公开标识。客户端禁止放 client secret、服务账户 JSON、后端管理员密钥。

宿主的 AppConfig 保存本应用 backendURL（结尾 `/adbox` 或 `/rightflow`）、iOS client ID、server/web client ID。注册 `GoogleSignInConfiguration.reversedURLScheme` 为 `CFBundleURLTypes` 中的 `CFBundleURLSchemes`。每个进程只组合一个 Google provider；官方 SDK 的 sharedInstance 是进程级状态。

```swift
import AuthCore
import AuthGoogleIOS

// 本段位于宿主 @MainActor 组合根；所有值来自宿主 AppConfig。
let googleConfiguration = try GoogleSignInConfiguration(
    iOSClientID: AppConfig.googleIOSClientID,
    serverClientID: AppConfig.googleServerClientID
)
let provider = GoogleSignInProvider(configuration: googleConfiguration) {
    // 宿主保存当前 scene 的可呈现控制器；不从全局窗口猜测。
    AppPresentation.currentViewController
}
let backend = try AppCloudAuthClient(baseURL: AppConfig.authBackendURL)
let tokenStore = try KeychainRefreshTokenStore(
    namespace: AppConfig.bundleID,
    backendURL: AppConfig.authBackendURL
)
let auth = AuthSessionStore(
    backend: backend,
    provider: provider,
    tokenStore: tokenStore,
    deviceID: try AuthDeviceIdentity.loadOrCreate(namespace: AppConfig.bundleID)
)
```

根视图持有并注入 `AuthSessionStore`。启动时 `try await auth.restore()`；用户点击登录时 `try await auth.signIn()`。根视图 `.onOpenURL { provider.handleURL($0) }` 转交回调。读取 `auth.session?.user` 与 `accessToken`；业务请求发现 access token 临近过期或被拒绝时显式 `try await auth.refresh()`，然后重试业务请求一次。库不设置后台定时器，不承诺系统挂起期间自动刷新。

`GoogleSignInProvider` 原样抛出 SDK 取消/失败错误，宿主可将 Google 的用户取消视为正常退出。`AuthError.errorDescription` 使用宿主 xcstrings 的以下 key：

| key | 中文 | English |
| --- | --- | --- |
| auth_err_configuration | 登录配置不完整 | Sign-in configuration is incomplete |
| auth_err_response | 登录服务返回无效数据 | The sign-in service returned an invalid response |
| auth_err_signed_out | 请重新登录 | Please sign in again |
| auth_err_superseded | 登录状态已变更，请重试 | Sign-in state changed. Please try again |
| auth_err_storage | 无法安全保存登录状态 | Unable to securely save the session |
| auth_err_server | 登录服务暂不可用 | The sign-in service is unavailable |

## 后端 HTTP 契约

`baseURL` 的路径前缀不会被 `/api` 替换。例如 `https://example.com/adbox` 的交换地址是 `https://example.com/adbox/api/v1/auth/google`。生产要求 HTTPS；HTTP 仅允许 localhost / 127.0.0.1 / ::1。

| 请求 | body / header |
| --- | --- |
| POST `{baseURL}/api/v1/auth/google` | `{"id_token":"Google ID token","device_id":"UUID"}` |
| POST `{baseURL}/api/v1/auth/refresh` | `{"refresh_token":"opaque token"}` |
| POST `{baseURL}/api/v1/auth/logout` | `Authorization: Bearer <access token>`，无 body |

成功必须为 HTTP 2xx，eapi `code` 为字符串 `SUCCESS`。交换及刷新结果：

```json
{
  "code": "SUCCESS",
  "message": "ok",
  "data": {
    "access_token": "opaque access token",
    "refresh_token": "opaque refresh token",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "00000000-0000-0000-0000-000000000001",
      "email": null,
      "display_name": null
    }
  },
  "timestamp": "server timestamp"
}
```

refresh 永久失效：HTTP 401 / `REFRESH_TOKEN_INVALID`；库清掉本地会话与 refresh token。网络暂不可用保留 refresh token供后续重试。Google 配置缺失与网络不可用由后端分别返回 `GOOGLE_NOT_CONFIGURED` / `GOOGLE_UNAVAILABLE`；客户端通过 `AuthError.server` 保留错误 code，服务内部 message 不直接显示。

## 存储、退出与并发

只把应用 refresh token 存入 Keychain，使用 `AfterFirstUnlockThisDeviceOnly`，不同 app namespace 与完整 backend URL 哈希隔离。每个组合根只支持一个活动账号；换账号时写入会覆盖该槽位，避免遗留上一账号 refresh token。access token 和后端用户只在内存。Google 自有凭证由 SDK 管理。

设备 UUID 保存在命名空间隔离的 UserDefaults，只是安装标识，不证明设备可信或用户已登录。不要把 token、HTTP body 或认证 header 放入日志。

退出先失效所有在途操作、清内存、登出 Google、删除本地 refresh，再尝试后端 logout。网络失败会抛错，但本地仍保持退出；Keychain 删除失败仍会尝试服务端撤销，并抛出存储错误，宿主应提示并重试。两个步骤都失败时 `AuthCleanupError` 保留两份错误。

generation 防止迟到登录/刷新重新写入；在途请求不主动取消，返回新 access 后会尝试撤销该新会话，避免旧 access 已因轮换失效而无法撤销。Keychain 保存新 refresh 失败时也尝试撤销刚返回的新会话。refresh 使用 single-flight 避免并发消费一次性 refresh token。网络失联或请求提交状态未知时只能保证内存退出，不能保证服务端已撤销；仍须遵守服务端有效期与会话管理策略。

## 依赖与验收

当前根 manifest 固定 GoogleSignIn-iOS **9.1.0 exact**，与统一仓库既有消费者兼容。宿主分发时保留 SDK 及传递依赖的许可证/NOTICE；无需把 SDK 源码复制进业务应用。下方 2026-10-20 的选型来源保留为初始 9.0.0 的历史记录。

2026-10-20 选型核验：以下新依赖均为 Apache-2.0，正式 release 已超过 7 天。GoogleUtilities 8.1.5 于 2026-10-14 发布，未满 7 天，根 manifest 约束为 8.1.4，避免间接选入。

| 依赖 | 版本 | 官方发布日期 |
| --- | --- | --- |
| AppAuth-iOS | 2.1.0 | [2026-06-12](https://github.com/openid/AppAuth-iOS/releases/tag/2.1.0) |
| AppCheck | 11.3.2 | [2026-09-14](https://github.com/google/app-check/releases/tag/11.3.2) |
| GTMAppAuth | 5.0.0 | [2025-05-01](https://github.com/google/GTMAppAuth/releases/tag/5.0.0) |
| GTMSessionFetcher | 3.5.0 | [2024-06-27](https://github.com/google/gtm-session-fetcher/releases/tag/v3.5.0) |
| GoogleUtilities | 8.1.4 exact | [2026-09-30](https://github.com/google/GoogleUtilities/releases/tag/8.1.4) |
| Promises | 2.4.1 | [2026-06-09](https://github.com/google/promises/releases/tag/2.4.1) |
| Interop for Google SDKs | 101.0.0 | 无 GitHub release；[官方 tag](https://github.com/google/interop-ios-for-google-sdks/tree/101.0.0) 对应 commit 日期 2024-12-06 |

来源：[官方发行](https://github.com/google/GoogleSignIn-iOS/releases/tag/9.0.0)、[9.0.0 许可证](https://github.com/google/GoogleSignIn-iOS/blob/9.0.0/LICENSE)、[服务端认证](https://developers.google.com/identity/sign-in/ios/backend-auth)、[URL scheme 接入](https://developers.google.com/identity/sign-in/ios/start-integrating)。

先通过环境变量 `DEVELOPER_DIR` 指向已安装 Xcode 的 Developer 目录；iOS 编译前设置 `IOS_SIMULATOR_SDK="$(xcrun --sdk iphonesimulator --show-sdk-path)"`。

测试命令：`swift test --filter AuthCoreTests`。用例清单位于 `ios/Tests/AuthCoreTests/TEST_CASES.md`。

2026-10-21 迁移目标验证：统一仓库根目录完整 `swift test` **43 项通过、0 失败**，包含 `AuthCoreTests` **18 项**；使用真实 Xcode iPhoneSimulator SDK、`arm64-apple-ios17.0-simulator` 在独立 `.build-ios` 目录编译 `AuthGoogleIOS`（包含官方 SDK 与传递依赖）通过。迁移证据见 `docs/migration-reports/apple.md`。复现目标编译：

```bash
swift build \
  --target AuthGoogleIOS \
  --scratch-path .build-ios \
  --triple arm64-apple-ios17.0-simulator \
  --sdk "$IOS_SIMULATOR_SDK"
```

GoogleUtilities 是为传递依赖新鲜度约束而显式声明，SPM 会提示根包未直接使用其 product；实际 SDK 通过 AppCheck 使用该依赖。

单测与模拟器编译不等于 Google OAuth 实际验收。宿主接入后仍需真实 Google OAuth client/bundle ID、URL scheme、后端 audience 配置，完成登录、用户取消、冷启动恢复、refresh 轮换、退出、断网退出与换账号操作验证。
