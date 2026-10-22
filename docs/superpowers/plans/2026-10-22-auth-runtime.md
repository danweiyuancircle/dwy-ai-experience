# 通用认证运行时实施计划

> 执行：主会话集成，独立文件由并行任务实现，完成后统一审查。用户已明确要求实施；不提交、发布或部署。

**目标：** 提供应用自建用户、可替换 JWT/会话、邮箱/用户名密码和可扩展第三方认证，并由 ADBox 后端验证接入。

**架构：** AuthRuntime 复用现有邮箱 challenge 与密码机制，应用注入 SubjectAdapter。SessionBackend 管理完整会话生命周期，默认实现使用 python-jose 与数据库 refresh 轮换。dwyeapi.auth 提供协议适配和现有邮件发送，认证核心不依赖 EAPI。

**技术栈：** Python 3.11、FastAPI、SQLAlchemy async、Pydantic、bcrypt、现有 python-jose 和 Google 官方验签；不新增自研协议实现。

**设计依据：** docs/auth-library-design.md 与本会话最后确认的可替换会话时序。

## 全局约束

- app_id 来自运行时；用户 subject 由应用提供，不要求固定 User ORM。
- auth extra 自动包含 email；核心只依赖邮件协议，保持单向包依赖。
- 公开接口无需登录；无效 Bearer 不降级匿名；权限与资源检查由应用负责。
- 邮件投递复用现有 Provider；验证码消费和业务用户写入同事务。
- 现有 Google/邮箱接口及 UUID 合同通过兼容装配保留。
- 不实现手机号、量化迁移、新业务同步、管理端改版或客户端登录 UI；ADBox 后端提供可实际调用的首个接入，客户端既有离线行为不变。
- 不改版本、不打标签、不发布、不读写生产数据；真实邮件/OAuth需要部署配置后验收。

## 审查重点

- 两个不同 User 模型、两个应用实例不能串配置或账号。
- 自定义会话实现的 issue/verify/refresh/revoke 全链路可替换。
- 注册失败不得留下半创建用户或已消费 challenge。
- JWT 过期/用途混用/跨应用、refresh 重放和退出撤销必须被拒绝。
- 安装 auth extra 自动获得邮件依赖；独立认证 wheel 不依赖隐式本机 EAPI 安装。

## 任务 1：会话合同与默认实现

文件：backend/packages/app-auth/src/dwy_app_auth/contracts.py、session_storage.py、session_backend.py；对应 tests/test_session_backend.py。

- [x] 先写真实数据库行为测试：JWT claims、跨应用拒绝、同一 refresh 轮换及重放撤销、注销与事务回滚。
- [x] 运行并记录缺功能失败。
- [x] 实现 VerifiedIdentity/AuthPrincipal/SessionTokens/SessionBackend，默认 JWTSessionBackend，不耦合用户表。
- [x] 运行新测试和相关会话回归。

## 任务 2：认证核心与用户适配

文件：backend/packages/app-auth/src/dwy_app_auth/runtime.py、runtime_storage.py、subjects.py、providers.py、passwords.py；对应 runtime 测试。

- [x] 先写两种应用 User 模型、自定义 SessionBackend、方法开关、邮箱/用户名、challenge 重放与失败回滚测试。
- [x] 运行并记录预期失败。
- [x] 复用现有 EmailAuthMixin 的 challenge/rate 原语，覆盖用户相关流程，接入应用 SubjectAdapter。
- [x] 实现第三方映射与显式绑定保护，Google 使用现有官方验证器。
- [x] 运行核心测试及已有邮箱/Google回归。

## 任务 3：EAPI 集成与独立制品

文件：backend/src/dwyeapi/auth.py、backend/tests/test_auth_runtime.py；认证包公开入口与依赖清单；ci 锁文件。

- [x] 先写 HTTP 注册登录刷新退出、自定义会话、公共/可选认证、跨应用与失败响应契约测试。
- [x] 实现实例化依赖与路由装配，映射应用 profile；复用 ApiResponse 和邮件组件。
- [x] 解除新核心对 EAPI 的反向依赖，旧 HTTP/服务保留显式惰性兼容。
- [x] 构建实际 wheel，在隔离环境安装/导入，验证 extra 解析与独立核心。

## 任务 4：ADBox 后端首个应用适配

文件：应用仓库 backend/packages/adbox-server 的工厂、应用账号 adapter、显式 Alembic 迁移，以及宿主类型化邮箱/JWT 配置和测试。

- [x] 先写旧 UUID 保护、邮箱闭环、Google启用、公开健康、认证拒绝和权限边界测试。
- [x] 接入独立业务账号模型与新 runtime；保留 IAP/sync 的身份合同，关闭未配置通道。
- [x] 提供新迁移与旧 auth_users 映射，迁移只由部署步骤显式执行。
- [x] 使用本轮构建制品验证，不以旧冻结 wheel 或 editable 缓存替代。

## 任务 5：统一审查与交付

- [x] 执行认证完整测试、EAPI相关测试、ADBox后端测试与 Ruff。
- [x] 独立审查改动，修复阻断性问题；检查敏感内容、diff范围和空白。
- [x] 更新安装/接入说明、测试清单与真实验收边界。
- [x] 交付本地变更和执行说明；不将未运行的真实邮件/OAuth或生产迁移称为通过。
