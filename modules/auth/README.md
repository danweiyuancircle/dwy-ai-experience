# 认证模块

认证按调用端和会话类型拆分，应用数据库与商品/业务规则由宿主维护。

| 位置 | 产品 / 包 | 用途 |
| --- | --- | --- |
| `modules/auth/apple/Sources/AuthCore` | SwiftPM `AuthCore` | Google 用户会话、HTTP 协议、刷新凭据 Keychain 存储；iOS/macOS 共用 |
| `modules/auth/apple/Sources/AuthGoogleIOS` | SwiftPM `AuthGoogleIOS` | iOS Google SDK 呈现与 ID token 获取 |
| `modules/auth/backend` | Python `dwy-app-auth` / `dwy_app_auth` | 基于 EAPI 的 Google 用户认证与独立管理员 Cookie 认证 |
| `modules/auth/web` | npm `@dwydev/auth-web` | 现有管理员登录组件、会话与同源 Cookie API |

Google 用户 token 与管理员 Cookie 不互相接受。此模块未增加邮箱验证码、Apple 登录或 Google Web 登录。Google OAuth client ID 等运行配置由各宿主注入，不能放入可复用默认配置。

Apple 从仓库根 `Package.swift` 选择同名 product。私有包下载、校验和安装见 `docs/private-distribution.md`；各端的配置接口见对应模块文档。
