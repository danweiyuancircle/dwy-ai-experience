# 认证模块

认证按调用端和会话类型拆分，应用数据库与商品/业务规则由宿主维护。

认证包按平台归入 `backend/`、`frontend/`、`ios/`；本文件保留跨端入口总览，包名、公开 API 和宿主装配方式不随目录调整改变。

| 位置 | 产品 / 包 | 用途 |
| --- | --- | --- |
| `ios/Sources/Shared/AuthCore` | SwiftPM `AuthCore` | 邮箱密码与 Google 用户会话、HTTP 协议、刷新凭据 Keychain 存储；iOS/macOS 共用 |
| `ios/Sources/iOS/AuthUI` | SwiftPM `AuthUI` | 邮箱密码登录、验证码注册自动登录、密码重置；自带中英文 SwiftUI 页面 |
| `ios/Sources/iOS/AuthGoogleIOS` | SwiftPM `AuthGoogleIOS` | iOS Google SDK 呈现与 ID token 获取 |
| `backend/packages/auth` | Python `dwy-auth` / `dwy_auth` | 基于 EAPI 的邮箱密码/Google 用户认证、可选滚动续期与独立管理员 Cookie 认证 |
| `frontend/auth-web` | npm `@dwydev/auth-web` | 现有管理员登录组件、会话与同源 Cookie API |

用户 token 与管理员 Cookie 不互相接受。邮箱验证码由应用数据库原子核销、eapi 邮件通道发送；本轮未增加 Apple 登录或 Google Web 登录。邮件密钥、验证码HMAC密钥、会话策略与 Google OAuth client ID 等运行配置由各宿主注入，不能放入可复用默认配置。

所有 iOS/macOS 代码统一在 `ios/`，从仓库根 `Package.swift` 选择同名 product；邮箱组件见 `ios/Docs/EMAIL_PASSWORD_AUTH.md`，Google 接入见 `ios/Docs/GOOGLE_AUTH.md`。Node/Python 包公开发布，Apple 继续使用私有 Git SwiftPM；分发与安装见 `docs/private-distribution.md`，各端的配置接口见对应模块文档。
