# 通用后端认证库设计

日期：2026-10-22。状态：用户确认实施；以 ADBox 后端作为首个应用适配，尚未发布。

## 1. 目标与边界

为多个 Python/FastAPI 应用提供可复用、可扩展的认证能力，通过 `dwyeapi[auth]` 统一安装，自动包含现有 email 依赖。应用选择启用方式，前端按场景组织页面；服务端独立强制执行启用策略。

首期包含邮箱标识＋密码、用户名＋密码、邮箱注册验证、忘记密码、已登录改密、第三方身份认证与关联、会话刷新和撤销。Google 为第一个真实第三方适配器；其他 Provider 通过相同边界逐个实现和验收。手机号认证后续新增适配，本期不加入短信依赖。

邮箱验证码登录与注册验证码不是同一功能；首期注册验证和找回密码必须具备，免密验证码登录不因存在发码接口而自动启用。

用户资料、业务用户表、角色权限、会员、额度、订单、隐私协议内容归应用。auth 不要求应用继承固定 User ORM，不创建携带这些业务字段的通用用户表。

ADBox 继续可选登录、离线使用；认证服务负责联网认证，客户端本地功能不依赖认证服务可用性。

## 2. 设计依据

已核对的代码基线：dwy-shared `9226fd155166bf926951762a39c7b399547af5e5`；ai-quant develop `6e54f25f83daf779701ab4d17ec87f86c8544356`。

- `backend/packages/app-auth/src/dwy_app_auth/email_auth.py:45`：发送适配已调用 EAPI 现成 `send_verification_code`；auth 管理用途隔离的 challenge。
- `backend/packages/app-auth/src/dwy_app_auth/email_auth.py:371`：密码重置、验证码消费、旧会话撤销已有同事务基础。
- `backend/packages/app-auth/src/dwy_app_auth/storage.py:28`：当前用户表仍以 `google_subject` 表示单一第三方，需要推广为独立外部身份。
- 参考项目 quant-cloud 的 `backend/packages/dwy-auth/src/dwy_auth/services/user.py:112`：现有密码登录按邮箱查询，不能直接称为已有用户名登录。
- 参考项目 quant-cloud 的 `backend/packages/dwy-auth/src/dwy_auth/models.py:12`：现有 User 包含角色、资料等字段，需要拆开认证与业务模型。
- 参考项目 quant-cloud 的 `backend/packages/dwy-auth/src/dwy_auth/protocols.py:21`：已有用户生命周期 Hook，可作为应用接入设计参考。
- 参考项目 quant-cloud 的 `backend/packages/dwy-auth/src/dwy_auth/__init__.py:42`：模块级注册状态不适合多应用实例，需要改为实例注入。

方案采用现有共享库的 challenge 与会话基础，吸收 cloud 的改密、换绑、限流及生命周期经验；不把旧实现逐文件复制成第三套。量化 cloud 目前没有可直接复用的第三方 OAuth 登录实现。

## 3. 分层与依赖

依赖方向：应用 → `dwyeapi.auth` 集成入口 → `dwy_app_auth` 认证核心；EAPI 的现有 email 组件通过协议注入认证核心。

| 层 | 职责 |
|---|---|
| `dwy_app_auth` | 认证流程、凭据、challenge、会话、Provider 与认证结果类型 |
| `dwyeapi.auth` | EAPI 响应/错误映射、邮件适配、FastAPI 装配与统一导出 |
| `dwyeapi` email | 邮件 Provider、模板、投递及厂商 SDK |
| 应用 | 业务用户适配、用户资料、接口权限、数据库迁移与产品策略 |

`dwy_app_auth` 不再反向导入整个 `dwyeapi`；必要的认证 DTO、错误和协议放在认证包，集成层负责转换。独立认证包注入 EmailCodeSender；EAPI 使用现有 Provider 实现此协议，继续复用发送通道与模板。

安装目标为 `dwyeapi[auth]`，其 extra 同时聚合认证包和 `dwyeapi[email]`；基础 `dwyeapi` 安装不强制安装认证依赖。安装 extra 不自动挂载路由，也不代替邮件凭据与运行时配置。

这样保持独立认证包与单向依赖，不引入 `dwyeapi ↔ dwy-app-auth` 的版本环。此前“认证包精确依赖整个 EAPI”的结构需要在本次设计中调整，不能只增加 extra 声明。

## 4. 对外入口

以下为本轮源码实现接口；尚未发布，安装与验收记录见认证包 README。

应用创建一个 `AuthRuntime` 实例，显式注入：

- 可信 `app_id`、启用的认证方式及 Provider 配置。
- SQLAlchemy 异步 session 工厂和认证表映射。
- `SubjectAdapter`，用于创建业务用户标识及检查主体状态。
- `EmailCodeSender`、密码策略、challenge 与会话策略。

首期支持 SQLAlchemy 异步事务，与两套现有后端技术栈对齐；应用仍可使用自己的 ORM 模型和内部主键。

核心入口控制为：

| 接口 | 契约 |
|---|---|
| `AuthRuntime` | 每个应用独立的认证服务实例；不使用模块级全局配置 |
| `install_runtime_auth(app, runtime, profile_loader=...)` | 返回 AuthBinding；统一类型化请求、错误与输入上限，未启用方式由运行时拒绝 |
| `AuthBinding.require_principal` | 验证凭据、应用归属、会话和主体状态，返回最小身份；失败返回 401 |
| `AuthBinding.optional_principal` | 无凭据时返回 None；存在但无效的凭据返回 401，不能静默降为游客 |
| `SubjectAdapter` | 应用用户创建与状态检查；不要求固定用户表 |
| `ExternalIdentityProvider` | 验证外部凭据，返回标准化且已验证的外部身份 |

流程服务提供注册、密码登录、发验证邮件、重置/修改密码、绑定/解绑身份、刷新、退出与撤销会话。HTTP 路由只做参数和 transport 适配，业务应用也可直接调用相同服务。

普通业务接口不会自动要求登录：应用自行选择是否使用上述依赖。公开接口、登录接口、权限接口可以并存。

## 5. 用户标识与资料归属

沿用“应用提供稳定 user_id”的边界。认证服务只认识 `subject`，将其视为不透明、稳定、限长的字符串，不假设它是应用 ORM 主键，也不把邮箱或用户名当作 subject。

`SubjectAdapter` 的最小责任：

1. 注册或首次外部登录时，在传入事务内创建应用主体并返回稳定 subject。
2. 按 subject 检查用户是否存在、是否允许认证；不存在或禁用时拒绝登录/访问。
3. 注销时另向 `runtime.delete_account(principal, cleanup=...)` 传入应用清理回调，与认证删除共用事务。

应用可以继续使用整数业务主键，并以现有 UUID 字段作为 subject。ADBox 保留现有 UUID 格式，Swift 客户端和 SyncCore 的 userID 约束不因库内部泛化而改变。

auth 的登录结果为最小 `Principal`：`subject`、`app_id`、`session_id`、认证方式；设备信息按 transport 的实际需要提供，不要求所有 Web 请求具有原生安装 UUID。昵称、头像、角色和会员信息由应用自己的资料接口返回。

同一自然人在不同 app_id 默认属于不同账号域。本库复用不表示多个产品共享用户或自动建立统一账号中心。

## 6. 认证数据

下表是存储职责，最终物理表及 Alembic revision 在实现设计中从现有表演进：

| 数据类别 | 内容与约束 |
|---|---|
| 登录标识 | app_id、subject、email/username 类型、规范化值、验证状态；同应用内唯一 |
| 密码凭据 | 每个 app_id/subject 一份密码哈希；邮箱和用户名登录复用同一密码 |
| 外部身份 | app_id、provider 配置、已验证 issuer、外部 subject 与本地 subject 的关联 |
| 验证 challenge | app_id、用途、目标标识、challenge ID、摘要、期限、尝试次数和消费状态 |
| 应用会话 | subject、app_id、会话期限、token 摘要、轮换/撤销及必要设备元数据 |
| refresh 重放记录 | 复用现有轮换和 family 重放撤销能力 |

这些表归认证库管理结构，但由应用决定数据库、metadata、表前缀和迁移执行。迁移不放在应用启动流程，不默认操作名为 users 的业务表。

app_id 必须进入所有查询与唯一约束；它来自宿主路由/运行时，不能信任请求 body 自报的应用域。邮箱、用户名的规范化规则需固定且可迁移，不静默更改存量 Gmail 别名规则。登录用户名与可修改的展示昵称明确分开。

## 7. 认证方式扩展

邮箱和用户名主要是两种标识，密码哈希、校验、失败控制、会话建立共用同一套流程。邮箱额外承担验证和找回渠道；只有用户名且没有已验证恢复渠道的账号，不能直接执行邮箱找回。

首期把能力拆为密码认证、邮箱验证流程、外部身份适配三类。后续手机号新增标识、发送/验证适配和相应流程，不修改业务 User，不强制现有应用安装短信 SDK。

第三方适配输出经过验证的身份：Provider 配置、issuer、稳定外部 subject、可选且已验证的邮箱。OIDC 使用验证后的 issuer＋sub，不将显示邮箱或 Provider 名称当作全局身份。

Google 沿用官方验签实现；原生 SDK 的 ID token 登录与浏览器授权码回调使用不同 transport，但汇入同一身份关联和应用会话流程。浏览器流程必须使用成熟 OAuth/OIDC 库处理 state、PKCE、nonce、回调地址等要求；Authlib 是待评估候选，本设计不新增手写协议实现。

新 Provider 应新增适配器及真实契约测试，注册到应用实例；不能宣称所有 OAuth Provider 都只需改配置。首期保证 Google，其他 Provider 逐个接入。前端可以查询服务器启用的能力；隐藏按钮不构成后端禁用。

一个 subject 可以关联多个已证明归属的登录标识和外部身份。同邮箱不自动合并；绑定需证明当前身份和新身份，解绑不得移除最后一种可用认证方式。敏感操作的重新认证结果应短期、限用途且可核销。

## 8. 邮件、验证码与事务

邮件投递继续调用 EAPI 现有 `send_verification_code`，共用邮件 Provider 和模板。认证库不复制邮件 SDK，不把 EAPI 原有 Redis 验码与认证数据库 challenge 同时作为真值来源。

验证码生成、用途隔离、尝试次数、期限与核销由认证库统一负责；注册、重置及换绑使用不同用途。发送成功才将对应 challenge 激活；发送失败返回明确失败，不显示发送成功。保留 pending/active 等现有状态语义，避免网络发信期间持有数据库事务。

外部投递和数据库不能共同回滚；投递成功但激活失败时，验证码不可用，用户可重试。重发、冷却和失败补偿必须有明确结果，不承诺邮件与数据库的跨系统原子提交。

注册时的应用主体创建、凭据写入、验证码消费使用同一个数据库事务。SubjectAdapter 接收当前 session，不得自行 commit、close 或另开事务；失败整体回滚。

密码重置同事务消费验证凭证、更新密码、撤销旧会话；访问令牌撤销检查也必须及时生效。通知类事件在提交后触发，不决定认证是否成功。跨数据库的应用业务初始化不承诺同等原子性，本期采用同库事务。

## 9. 会话与接口权限

会话签发、刷新合并、token 哈希存储、轮换、重放撤销和退出复用已有实现。验证码证明、密码重置凭证和 access token 必须有不同用途与验证入口，不能互相代用。

认证核心统一处理会话，transport 决定返回方式：原生客户端使用 JSON token；Web 可使用 HttpOnly refresh Cookie，明确 Secure、SameSite、CSRF、Cookie path 与名称配置。不同应用不共用固定 Cookie 名或未隔离的密钥域。

会话实现通过 `SessionBackend` 注入，不强制项目采用库自签 JWT。默认提供短期 JWT access 与轮换的不透明 refresh；已有项目可注入自己的签发、校验、刷新与撤销实现。凭据认证输出 `VerifiedIdentity`，会话校验输出 `AuthPrincipal`，同一应用的整个会话生命周期由所选实现负责，避免混用两套签发和撤销状态。

接口授权留在应用：

- 公开接口不挂认证依赖。
- 登录接口使用 `current_principal`。
- 特定权限接口组合应用自己的权限依赖。
- 资源接口继续检查归属、租户、对象状态等上下文。

auth 不定义 administrator、VIP、退款权限等业务含义，不附带统一 RBAC 表。不将长期 token 中的角色/会员快照作为应用动态权限的唯一来源。认证失败返回 401，身份有效但应用拒绝操作返回 403。

## 10. 策略与安全责任

应用可配置启用方式、Provider、密码规则、会话期限、邮箱域名准入、发码预算、登录失败限制和是否要求人机验证；共享库负责强制执行，而非仅由前端提示。

输入均类型化且限长/限大小，分页有上限；外部身份与重定向地址严格校验；敏感日志不写密码、token、验证码或 Provider 密钥。未知账号与错误密码的响应避免泄露账号存在性。

密码验证兼容已有哈希与存量账号；不通过静默改哈希或规范化强迫老用户改密码。首次支持的密码算法沿用成熟实现，算法调整需另外明确兼容和 rehash 策略。

图形验证码、ALTCHA 等作为可选安全适配；复用现有能力的安全边界，不使每个原生 App 强制依赖某个网页验证组件。具体使用场景由应用策略决定。

## 11. 接入与迁移顺序

1. 固定 SubjectAdapter、Principal、认证方式及 Provider 合同，完成依赖单向化与实例隔离。
2. 将现有邮箱密码、challenge、会话改接上述合同；补用户名标识，不重写密码流程。
3. 把现有 Google 身份迁入外部身份关联，保留用户 subject 与已有会话约定；补绑定/解绑安全规则。
4. 完成 `dwyeapi[auth]` 与 email 聚合、集成入口及可选路由。
5. 先以 ADBox adapter 验证通用能力；保持当前 UUID、API envelope 和客户端兼容，继续游客离线可用。
6. ai-quant 使用兼容路由和 SubjectAdapter 接入，保留内部用户主键、密码哈希与业务表；JWT、Cookie、旧会话与邮箱规则分别制定迁移期策略，不直接换库后宣称兼容。

量化的旧验证码/重置实现不能未经审查原样迁入；统一采用用途隔离、原子核销与 typed token 的认证核心。会员发放、额度初始化、API Key 签名、支付、用户资料和权限继续留应用或独立功能模块。

## 12. 验收与交付边界

至少覆盖：两个独立应用/运行时不串配置与账号；不同业务 User 模型均可接入；邮箱和用户名指向同一主体；未启用方式拒绝请求；邮件失败不返回成功；challenge 重放/用途混用被拒绝；注册失败整体回滚；重置凭证不能用于接口访问；重置撤销旧会话；同邮箱第三方不自动合并；绑定/解绑及最后凭据保护；退出/切号旧请求不能恢复会话；应用权限和资源归属检查。

需要真实 PostgreSQL 验证关键并发/事务，独立干净环境验证发布包依赖安装，并分别验收真实邮件、Google 登录和 Web/原生 transport。SQLite、fakeredis、受控 Provider 与源码检查不能替代这些结果。

本轮已实现源码与 ADBox 后端接入；未改发布版本、打标签或部署。Google 当前接收客户端取得的 ID token，不提供浏览器授权码重定向流程；Cookie transport、人机验证注入、可配置邮箱域名策略及跨库初始化属于后续扩展，不能按本文架构描述视为已交付功能。
