# Apple 登录：各应用独立配置，共享实现

Python 固定版本：`dwy-auth==0.1.1`、`dwyeapi[auth]==0.12.1`。SwiftPM 标签：`0.6.0`，链接 `AuthCore` 与 `AuthAppleIOS`。同时使用 Webhook 时安装 `dwy-webhooks==0.4.1`，避免旧包对 EAPI 的精确版本冲突。

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install 'dwyeapi[auth]==0.12.1'
```

不需要 App Cloud、某个产品源码、本机 wheel 或开发机路径。纯核心消费者只装 `dwy-auth==0.1.1`，自行选择 HTTP 框架；`dwy_auth.apple`、`dwy_auth.apple_auth`、`dwy_auth.apple_storage` 都是公开模块。

## 每个新应用提供什么

| 注入项 | 所属及用途 |
| --- | --- |
| `AuthRuntime.app_id` | 后端逻辑应用标识，不能由客户端任意选择；挑战、身份、会话、通知和队列按此隔离 |
| `AppleSignInConfig.client_id` | 该应用的 Apple audience；原生 iOS 使用自己的 Bundle ID |
| `team_id` / `key_id` / `private_key` | Apple Developer 中为该应用正确关联的登录 Key；只能配置在服务端 |
| `token_encryption_key` | 服务端持久化加密密钥，稳定保存并备份；重启时不能重新生成 |
| `metadata` / `sessions` / `subjects` | 应用自己的表声明、会话工厂和业务主体适配器 |
| `SessionBackend` / `profile_loader` | 应用自己的令牌/会话和资料合同 |
| iOS `baseURL` / `namespace` / 窗口 | 应用完整 URL、独立 Keychain namespace 和当前呈现窗口 |

同一进程可以托管多应用，但每个应用要有独立 runtime、Apple 配置与路由绑定。一个 runtime 只接受一个精确 Apple audience，不能把所有 Bundle ID 放进一个宽松白名单。同一 Apple 用户在不同应用中不按 email 自动合并；共享实现不等于跨应用共享账号或会话。

## 接入现有 AuthRuntime

以下变量均由宿主已有的应用工厂提供。`runtime` 已注册本应用的业务主体、数据库会话和 SessionBackend；`profile_loader` 返回本应用资料。

```python
from dwy_auth.apple import AppleGateway, AppleSignInConfig
from dwy_auth.apple_auth import AppleAuthService
from dwy_auth.apple_storage import build_apple_tables
from dwyeapi.auth import install_runtime_auth
from dwyeapi.auth_apple import install_apple_auth

# 在应用 metadata 装配阶段声明；只声明，不创建数据库结构。
apple_tables = build_apple_tables(metadata)
config = AppleSignInConfig(
    client_id=apple_client_id,
    team_id=apple_team_id,
    key_id=apple_key_id,
    private_key=apple_private_key,
    token_encryption_key=apple_token_encryption_key,
)
apple = AppleAuthService(
    runtime, apple_tables, AppleGateway(config),
    revoke_sessions=revoke_apple_sessions,
)
runtime.providers["apple"] = apple
binding = install_runtime_auth(app, runtime, profile_loader=profile_loader)
install_apple_auth(app, apple, binding=binding, profile_loader=profile_loader)
```

`revoke_apple_sessions(db, subject)` 必须在传入事务中撤销本应用、该 subject 的 Apple 会话及其刷新能力，不能提交或另开连接。使用默认 `JWTSessionBackend` 时，更新宿主 `SessionTables.sessions`，筛选 `app_id == runtime.app_id`、`subject == subject`、`method == "apple"` 后设置 `revoked_at`。其它会话实现需提供相同撤销语义；不能只删除本地登录按钮状态。

1. 将 `apple_tables` 的四张表加入宿主 Alembic metadata，生成并执行宿主迁移；库不自动建表。已有 runtime 的迁移历史继续使用。
2. 保留 `external` 方法组；只在 Apple 配置完整时装配 provider 和路由。通用 `authenticate("apple", credential=...)` 被拒绝，必须使用挑战和授权码的专用流程。
3. 宿主生命周期定期调用 `await apple.process_revocations()`。任务失败保留密文并退避，关闭时先停止工作器；Provider 资源通过 runtime 生命周期关闭。
4. 删号时，在 `runtime.delete_account(..., cleanup=...)` 的同一 cleanup 事务内调用 `await apple.prepare_delete(db, subject)`，再删除业务数据。提交后运行撤销工作器；上游仍待重试时应明确返回 pending。存在授权/撤销任务期间不能移除配置、换加密密钥或提前删除队列表。
5. 各应用在 Apple Developer 开启自己的 Sign in with Apple，关联登录 Key，并保存该应用完整 HTTPS 账号通知 URL，例如 `https://api.example.com/my-app/api/v1/auth/apple/notifications`。这些步骤无法由通用 SDK 自动完成。

通知接口接收 `{"payload": "<Apple signed JWT>"}`，由库验签并验证该应用的 issuer/audience/time。外层挂载路径由宿主决定；Swift 客户端保留 `baseURL` 中的全部前缀。Swift SDK 使用默认 `/api/v1/auth` 合同；自定义整个认证路径时需提供自己的 `AppleAuthBackend`。

## 复现验收

- 在仓库外新建虚拟环境，从正式 PyPI 安装以上精确版本；导入 `dwy_auth.apple`、`dwy_auth.apple_auth`、`dwyeapi.auth_apple`，确认导入来自该环境的 site-packages。
- 用自己的逻辑 app_id、Bundle ID、用户模型和数据库运行挑战、登录、重复挑战拒绝、撤销通知、删号及 worker 重试；另一应用的挑战与凭据必须被拒绝。
- iOS 按 [原生接入说明](../ios/Docs/APPLE_AUTH.md) 使用自己的 URL/namespace/窗口；nonce 原样交给 Apple，后端兑换后才建立业务会话。
- 最后用真实 Apple ID 和签名真机验收。单测中的受控 Apple 响应、包安装成功或模拟器编译均不能代替这一步。

私钥、Apple refresh token、client_secret 和加密密钥不能进入 iOS、Git、公开示例或日志。不要直接 JSON 序列化含 `SecretStr` 的配置用于部署；默认序列化会将密钥掩码，部署工具应明确读取 SecretStr 原值并通过保密通道注入。
