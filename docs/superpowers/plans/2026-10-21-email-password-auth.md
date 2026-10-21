# 邮箱密码认证组件实施计划

**目标：** 实现邮箱密码登录、邮箱验证码注册后自动登录、密码重置和可配置的活跃会话续期，提供可复用 iOS UI。
**规格：** `docs/ios-email-password-auth-analysis.md`，邮箱作为账号；用户已明确要求开始实现。
**执行：** 按已授权范围持续实施，后端与 Apple 核心按下列协议并行，UI 消费核心。保留已有未提交目录迁移，不自动提交、发布或修改 ADBox 客户端。

## 公共协议

- `POST /api/v1/auth/email/code`：`email,purpose`；purpose 为 `register` 或 `password_reset`。data 返回 `challenge_id,expires_in,resend_after,code_length`。
- `POST /api/v1/auth/register`：`email,password,code,challenge_id,device_id`；返回现有 TokenResponse。
- `POST /api/v1/auth/login`：`email,password,device_id`；返回现有 TokenResponse。
- `POST /api/v1/auth/password/reset`：`email,password,code,challenge_id`；返回 data `{status:"completed"}`，撤销旧会话。
- 保留现有 Google/refresh/logout 接口及 SUCCESS 信封；access 为 900 秒。长期策略显式启用后 refresh 滚动 180 天，默认旧策略不变。
- Swift：`EmailCodePurpose`、`EmailCodeChallenge(challengeID,expiresIn,resendAfter,codeLength)`；AuthSessionStore 新增 `sendEmailCode(email:purpose:)`、`signIn(email:password:)`、`register(email:password:code:challengeID:)`、`resetPassword(email:password:code:challengeID:)` 与 `refreshIfNeeded()`，均 async throws。

## 任务

- [x] 后端：先写失败测试，新增邮箱凭据/验证码事务/密码 API；复用 eapi bcrypt 和邮件 provider；按应用用途隔离、原子核销、发送/验证/登录限流；删号清理凭据。测试注册、登录、重置、隔离、重放、既有 Google 回归。
- [x] 会话策略：先写跨月/滚动期限/历史限额测试，显式配置滚动策略，清理历史，保持撤销和重放检测。不能因累计正常刷新达到4096次而强制重登。
- [x] AuthCore：先写 HTTP 与会话测试；不依赖 Google provider 即可使用邮箱；同一安装路径处理 token，旧回调/并发刷新/Keychain失败回归。
- [x] AuthUI：新增 SwiftUI AuthFlowView、流程状态模型与资源，登录/注册/重置三页；中文英文、自动填充、键盘、错误恢复；提供宿主集成示例与接口说明。
- [x] 集成验证：后端全套认证测试及 lint；Swift 包测试和 iOS simulator 构建；检查无关变更与凭据。真实 Resend/OAuth/业务端接入分别报告，不以本地验证替代。

## 优先审查

注册后安装会话失败；后台返回覆盖退出/换号；验证码跨应用用途复用；超长UTF-8密码；刷新历史/响应丢失导致提前退出。

## 执行记录

- 开始：确认当前工作区迁移由用户保留；实现直接基于当前目录，不覆盖或整理既有改动。
- 规则：不新增运行时依赖，复用现有 eapi/SwiftUI；不自动发布或提交。
- 变更：验证码改由数据库事务核销，复用邮件传输而不引入Redis；开发测试额外使用Alembic 1.18.4验证旧表迁移，运行时不新增依赖。
- 审查修正：注册安装失败的专用错误、重置密码后本地清理和迟到请求失效、发送延迟后的验证码剩余时间，均补RED→GREEN回归。
- 已验证：认证后端69通过/2个PostgreSQL条件跳过，eapi253通过，AuthCore40通过，AuthUI10通过，Swift完整包测试通过，示例iOS模拟器构建与XCUITest通过。
- 边界：真实Resend、生产PostgreSQL、私有包分发、app-cloud部署和ADBox客户端接入未执行。
- 产物验收：显式构建本轮eapi/auth wheel，全新venv离线安装，隔离模式完整smoke通过；实际导入来源site-packages，固定6表与新邮箱能力均验证。
