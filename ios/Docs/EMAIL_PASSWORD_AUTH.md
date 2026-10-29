# 邮箱密码认证组件

SwiftPM 产品：`AuthCore`、`AuthUI`。iOS 与 macOS 共用邮箱表单、Google 官方控件与 Apple 登录入口；宿主提供同一账号仓储的业务动作。

## 宿主接入

```swift
import SwiftUI
import AuthCore
import AuthUI

@MainActor
struct SignInScreen: View {
    let session: AuthSessionStore
    let onSuccess: (AuthUser) -> Void

    var body: some View {
        AuthFlowView(
            session: session,
            configuration: AuthUIConfiguration(appName: "My App"),
            onAuthenticated: onSuccess
        )
    }
}
```

宿主只创建一个 AuthSessionStore，并与业务 API 共用。初始化使用真实应用后端的完整 URL（包含产品前缀）：

```swift
@MainActor
func makeAuthSession(baseURL: URL, namespace: String) throws -> AuthSessionStore {
    let client = try AppCloudAuthClient(baseURL: baseURL)
    let tokenStore = try KeychainRefreshTokenStore(namespace: namespace, backendURL: baseURL)
    let deviceID = try AuthDeviceIdentity.loadOrCreate(namespace: namespace)
    return AuthSessionStore(backend: client, tokenStore: tokenStore, deviceID: deviceID)
}
```

生产后端必须 HTTPS。namespace 使用应用自己的稳定标识；相同服务器不同产品必须保留不同 URL 前缀。不要跨 App 共用会话，不保存密码。

宿主负责关闭页面、配置 `.tint` 和 `.environment(\.locale, ...)`。组件自带中英文资源，不要求每个宿主复制认证页面文案。`AuthUIConfiguration` 可注入服务协议与隐私政策 URL。

冷启动显式 `try await session.restore()`；进入前台或受保护业务请求前执行 `try await session.refreshIfNeeded()`。无已登录会话且无恢复凭据时，不应启动反复刷新或弹网络错误。参考 `ios/Examples/EmailPasswordAuth/EmailPasswordAuthApp.swift` 的启动与页面呈现顺序。

## 用户流程

- 登录：邮箱＋密码，不发送验证码。
- 注册：填写邮箱和密码，获取六位验证码，提交后直接安装后端会话。
- 找回密码：验证邮箱后设置新密码，成功后清理旧本地会话，返回登录。
- 注册已成功但会话保存失败：返回登录页，提示账号已创建，避免重复注册。
- 取消或关闭视图：失效未完成认证的回调，清空页面内存中的密码与验证码。

邮箱统一去除首尾空白并转小写，不修改 Gmail 点号或 `+tag`。新密码至少15个 Unicode 标量、最多72个 UTF-8 字节；密码不去空格、不截断。登录只要求非空且不超过72字节，以便兼容已有凭据。前后端均校验。

`AuthRegistrationError.installationError` 区分“注册失败”与“注册已完成、凭据安装失败”。调用 AuthCore 自建 UI 的宿主同样需要处理这个分支。

## 服务端与长期登录

服务端实现位于 `backend/packages/auth/src/dwy_auth/`；具体装配、错误码和迁移步骤见 `backend/packages/auth/README.md`。

- 邮箱功能通过 EmailAuthConfig 和 EmailCodeSender 显式装配；EapiEmailCodeSender 复用本轮 eapi 邮件传输接口与 Resend 模板。
- 验证码、尝试次数、限流使用应用数据库事务，不依赖 Redis；HMAC secret 由宿主密钥配置提供，所有 worker 一致，不写客户端。
- 老库需运行 `dwy_auth.migrations.upgrade_email_auth(op)` 对应的宿主 Alembic revision；共享库不在启动时自动迁移。
- 旧 Google 用户 UUID 和现有调用方式保留；不因邮箱相同静默合并账号。
- 默认会话仍是原30天固定期限。需要长期登录的宿主显式注入 `SessionPolicy(refresh_ttl=180 * 86400, rolling_refresh=True)`。
- access仍为15分钟；有效刷新顺延refresh空闲期。退出、重置、设备撤销、删号仍可使会话失效。
- 不通过后台心跳保活。超过180天不能成功联系认证服务时需重新登录。

短暂网络失败不删除本地 refresh token。服务器已轮换但客户端未收到/未保存返回值时，仍受一次性 refresh 和重放检测约束，不能保证任何弱网中断后都无需重新登录。

本组件不提供业务同步或付费权益判断。`AuthFlowView(actions:configuration:googleSignIn:appleSignIn:onAuthenticated:onCancel:)` 允许宿主注入业务动作。Google 凭据由 `AuthGoogleIOS` / `AuthGoogleMac` 获取；Apple 登录动作调用 `AuthSessionStore.signInWithApple(provider:)`，沿用服务端挑战、原始 nonce 与授权码兑换流程，见 `ios/Docs/APPLE_AUTH.md`。

需要业务准入的宿主给 `AppCloudAuthClient` 注入 `admissionProofProvider`。邮箱注册/登录、Google/外部登录、Apple 专用登录、refresh 和轮换会话的邮箱更新每次重新读取证明并提交 `admission_proof`，上限 131072 字节；失败时不发送身份凭据。发码和密码重置不附带证明。服务端显式配置 `AuthAdmission` 后，在同一业务事务内完成主体、准入绑定和会话签发。未配置此扩展的宿主行为不变。

业务动作成功后必须自行完成组合根恢复工作，不能只依赖页面完成回调；宿主因认证状态变化卸载表单时，组件会失效尚未完成的 UI 回调。

## 可运行示例与验证

`ios/Examples/EmailPasswordAuth/` 提供 XcodeGen 工程定义、真实HTTP宿主示例及 XCUITest。默认 `https://api.example.com/adbox` 为占位配置，需替换真实服务 URL 后才可注册收信。

在仓库根执行：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test --disable-automatic-resolution
PYTHONPATH=backend/packages/auth/src:backend/src backend/.venv/bin/python -m pytest backend/packages/auth/tests -q
```

在示例目录生成工程：

```sh
xcodegen generate
```

已有新源码不等于消费端已升级：需构建并分发匹配的 eapi/认证包，宿主迁移数据库并注入邮件、第三方身份和会话配置，SwiftPM 使用包含相应接口的不可变版本。本地验证不表示依赖已发布或服务已部署。

## 已登录账号管理

`AppCloudAuthClient` 同时实现独立 `AccountManagementAuthBackend`；旧 `AuthBackend` 和 `EmailPasswordAuthBackend` 实现无需新增方法。
宿主通过同一个 `AuthSessionStore` 调用：

- `listIdentities()` 返回 `[AuthLoginIdentity]`，根据 `kind` 判断邮箱、用户名或外部方式；外部身份附带 `provider/issuer/value`，用于精确解绑。
- `sendEmailUpdateCode(email:reauthentication:)` 发送当前账号专属的邮箱变更验证码。
- `updateEmail(email:code:challengeID:newPassword:)` 安装返回的轮换会话，保持当前 userId；首次添加邮箱密码时提交新密码。
- `bindExternal(provider:credential:reauthentication:)` 与 `unlinkIdentity(_:reauthentication:)` 复用服务端现有受重新认证保护的接口。

`AuthReauthentication` 使用 `.email(identifier:password:)`、`.username(identifier:password:)` 或 `.external(provider:credential:)`。
Google 的 provider 为 `google`，credential 为官方 SDK 本次获取的 ID token。
Apple-only 账号调用 `prepareAppleReauthentication(provider:purpose:)`，用途选择 `.emailUpdate`、`.bind` 或 `.unlink`，再把返回的 `AuthReauthentication` 交给对应管理接口。SDK 用当前会话领取绑定主体和用途的服务端挑战，把原始 nonce 交给原生授权，并在切号、刷新或取消时拒绝迟到材料。底层编码为 `method=external, identifier=apple`，`credential` 保留 `challenge_id`、`identity_token`、`authorization_code`；不会恢复旧的客户端 nonce 单令牌流程。
应用不得自己读写 Keychain、组装 subject、交换账号归属或按相同邮箱合并；旧入口保留到目标邮箱验证成功。
SDK 显式刷新当前 Bearer，邮箱变更只通过私有安装路径保存新 refresh，切号后迟到凭据会被拒绝并撤销。
主邮箱与 Google profile 邮箱具有不同语义；登录入口列表来自服务端，不能从当前登录按钮推测。

这些入口需要共享服务端 schema 与宿主 `EmailSubjectAdapter.update_email` 已交付；源码验证不表示依赖已正式发布或生产数据库已迁移。
