# 通用认证接入说明

`AuthRuntime` 由应用注入业务主体和会话实现；旧 `AuthService` 兼容入口继续保留，新项目使用运行时 API。Apple 登录接入见 [独立装配说明](apple-auth-integration.md)。

## 安装与依赖

使用 `pip install "dwyeapi[auth]==0.12.1"`，同时安装 `dwy-auth==0.1.1` 和现有邮件组件。独立 `dwy-auth` 不依赖 EAPI/FastAPI，应用可注入自己的邮件发送和会话实现。正式消费锁定 registry 版本，不能依赖开发机路径或同版本的工作区源码。

## 装配合同

- `build_runtime_tables(metadata, prefix="auth_runtime_")` 声明认证表；`register_session_tables` 声明默认会话表。宿主通过自己的 Alembic 历史执行迁移，库不自动建表。
- `SubjectAdapter.create_subject(db, registration)` 创建应用业务账号，返回稳定且最多 255 字符的 subject。`is_active(db, subject)` 检查主体，敏感写入需锁定业务账号行。回调不得提交、关闭或另开事务。
- `AuthRuntime(app_id, sessions, tables, subjects, session_backend=..., email_sender=..., email_config=..., providers=..., methods=...)` 为每应用独立实例，方法组选项为 `email`、`username`、`external`。
- `JWTSessionBackend(app_id, issuer, audience, secret, sessions, session_tables)` 默认 access 15 分钟、refresh family 30 天绝对到期；注入至少 32 字节密钥。也可注入完整 `SessionBackend`，覆盖签发、验证、刷新、撤销及同事务主体撤销。
- `GoogleIdentityProvider(OfficialGoogleVerifier(GoogleConfig(client_id=...)))` 注册为 `providers={"google": ...}`；核心调用 `authenticate("google", credential=id_token)`。当前仅 ID token 校验，不提供浏览器 OAuth 重定向。其他 Provider 实现 `ExternalIdentityProvider.verify` 后注册。
- 邮件复用 `EapiEmailCodeSender(make_email_provider(settings))` 与现有 `send_verification_code` 模板；认证库管理用途隔离的 challenge。宿主管理邮件 Provider 生命周期。
- 发码请求使用可选 `Accept-Language`（最长 512 字符）；出现有效且未被 `q=0` 排除的 `zh` / `zh-*` 时发中文，缺省、无效或其他语言发英文。主题、HTML、纯文本统一选择；语言逐次透传，不参与验证码身份与限流键。自定义 sender 的 `send` 和邮件 provider 的 `_send` 需接受 keyword-only `language="en"`；程序调用可指定 `send_email_code(..., language="zh")`。
- 中文主题继续配置 `resend.subject`，英文主题配置 `resend.subject_en`；英文品牌标语分别配置 `brand_tagline_en` / `brand_slogan_en`，缺省留空，不复用中文宣传文案。设备端应按当前语言显式传头，不依赖服务器的系统语言。

`install_runtime_auth(app, runtime, profile_loader=...)` 挂载以下接口并返回 `AuthBinding`。`profile_loader(AuthPrincipal)` 返回应用资料，JSON 的 `user` 不绑定固定业务表。装配会关闭 runtime 的 Provider 资源，外层生命周期避免重复关闭。

| POST 路径 | 主要输入 |
|---|---|
| `/api/v1/auth/email/code` | `email,purpose`，用途为 `register` 或 `password_reset` |
| `/api/v1/auth/register` | `email,password,code,challenge_id,device_id?` |
| `/api/v1/auth/login` | `email,password,device_id?` |
| `/api/v1/auth/username/login` | `username,password,device_id?` |
| `/api/v1/auth/username/bind` | Bearer + `username,password`，校验当前密码 |
| `/api/v1/auth/google` | `id_token,device_id?` |
| `/api/v1/auth/external/login` | `provider,credential,device_id?` |
| `/api/v1/auth/external/bind` | Bearer + `provider,credential,reauthentication` |
| `/api/v1/auth/identity/unlink` | Bearer + `kind,value,provider?,issuer?,reauthentication` |
| `/api/v1/auth/password/reset` | `email,password,code,challenge_id` |
| `/api/v1/auth/password/change` | Bearer + `old_password,new_password` |
| `/api/v1/auth/refresh` | `refresh_token` |
| `/api/v1/auth/logout` | Bearer |

`GET /api/v1/auth/capabilities` 返回方法组与已注册 Provider。`reauthentication` 为 `{method: "email"|"username"|"external", identifier, password?, credential?}`；external 的 identifier 为 Provider 配置名。解绑外部身份使用 `kind="external"`、provider 配置名、issuer 和外部 subject 作为 value。同邮箱不自动合并账户，不能解绑最后一个登录方式。

凭据认证返回五分钟、单次、限用途的内部 `VerifiedIdentity`；`runtime.issue(identity, device_id=...)` 核销证明并建立会话。HTTP 不接收客户端自报证明；密码重置或身份解绑后旧证明失效。新密码至少 15 字符、最多 72 UTF-8 字节，不裁剪密码。认证请求限 32 KiB，字段另有限长，验证错误不回显凭据。

## 应用权限与注销

公开接口不加依赖；需身份的接口用 `Depends(binding.require_principal)`；可选身份接口用 `Depends(binding.optional_principal)`。无凭据可匿名，有无效凭据返回 401。角色、会员、对象归属及其他权限由应用校验，拒绝返回 403。

`runtime.delete_account(principal, cleanup=...)` 在同库事务内撤销主体会话、删除认证凭据、执行应用回调；`cleanup(db, subject)` 不得自行提交。购买记录等保留数据由应用决定，认证库不擅自删除。

## 兼容与验证边界

旧 HTTP/服务依赖 EAPI，通过惰性导入加载。仅 Google 三表历史库使用 `build_auth_tables(metadata, include_email_auth=False)`；启用 legacy 邮箱需先执行对应迁移。

真实 SQLite/HTTP 覆盖邮箱、用户名、重置/改密、受控 Google Provider、绑定/解绑、默认 JWT、应用非 JWT 会话、匿名与应用权限。独立 wheel 安装验证无 EAPI 的 core 及聚合 extra。真实 PostgreSQL、邮件投递与 Google 账户交互需分别验收；受控 Provider 不代表真实 OAuth 通过。
