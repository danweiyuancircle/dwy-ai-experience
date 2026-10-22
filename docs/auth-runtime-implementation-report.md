# 通用认证实现与验收记录

日期：2026-10-22。仅本地实现、预览制品和后端验收；未提交、推送、改发布版本、打标签、发布或部署。

## 实现范围

- 分支：共享库 `feat/auth-runtime`；应用后端 `feat/adbox-auth`；ADBox 客户端保留 `feat/cloud-auth`，本轮不改 Swift/UI。
- `AuthRuntime`：邮箱验证注册、邮箱/用户名密码认证、重置/修改密码、第三方身份关联、二次认证、单次限用途证明及账户删除事务。
- `SubjectAdapter`：应用拥有业务用户和资料；subject 为稳定不透明字符串，ADBox 继续使用既有 UUID。
- `SessionBackend`：覆盖完整生命周期，可由应用替换；默认 JWT access 加轮换 refresh，撤销立即生效、重放撤销 family，单 family 轮换上限 4096。
- `dwyeapi[auth]` 聚合现有 email；独立认证核心去除对 EAPI/FastAPI 的反向依赖。邮件发送仍复用现有 Provider 与模板。
- Google 首个 Provider 使用既有官方验签器；当前提供 ID token 登录，未实现浏览器授权码重定向、手机号、Cookie transport 或业务权限系统。

## ADBox 接入

ADBox 新建自有 `adbox_accounts`，显式迁移 `38d814c9a501` 保留旧 UUID 和 Google sub。已有不透明会话不转换为 JWT，升级后重新登录。同步和 IAP 保留原 UUID 归属，账户注销保留购买历史。

注销同事务清理新认证身份、业务资料、同步数据，并对保留的 legacy 用户去标识、禁用和撤销旧会话。新建库没有 legacy 表时仍可注销。新旧表同时清理失败会回滚。

公开接口不要求认证；可选身份缺凭据时匿名，无效凭据返回 401。权限继续由应用校验。缺签名/邮箱/Google 配置时对应能力明确关闭，不生成临时生产密钥。ADBox 仅启用邮箱及已配置 Google，通用用户名能力由其他应用自行选择。

Quadrant、RightFlow 使用明确的 legacy Google-only 三表 profile，不引入邮箱迁移或改变其账户数据。

## 验证结果

| 层次 | 已执行结果 |
|---|---|
| 共享 EAPI 与认证包完整测试 | 398 passed，3 skipped；均为未配置 PostgreSQL |
| ADBox 所属后端独立 wheel 环境全量 | 337 passed，5 skipped；均为未配置 PostgreSQL |
| HTTP 新认证测试 | 8 项通过，包含应用自定义非 JWT 会话全生命周期 |
| 静态检查 | 两仓库涉及代码 Ruff、格式检查与 `git diff --check` 通过 |
| 独立 core wheel | 无 EAPI/FastAPI 环境真实异步 SQLite 注册、用户名、重置、轮换和退出通过 |
| 聚合 extra | 实际 wheel 安装可解析认证及 email/Resend；无 core 反向依赖 |
| 预览安装 | 全新环境 `uv sync --frozen --all-extras --no-editable --no-cache` 成功；认证、EAPI、ADBox、同步模块导入来自 site-packages |
| 三个独立应用安装包 | ADBox、Quadrant、RightFlow 各自全新环境通过独立迁移、固定必需表、生命周期、管理配置/审计检查；另两应用未安装，安装依赖检查通过 |

最终后端复核使用去除 `PYTHONPATH`、`PYTHONHOME` 的 Python `-I` 模式，包含修复后的当前解释器迁移子进程；已确认 Resend 为锁定的 2.49.1。测试不使用共享源码覆盖安装包。

本次本地临时目录中的测试日志：`dwy-auth-final-tests.txt`、`adbox-auth-frozen-final-verified.txt`。独立环境目录：`dwy-auth-artifacts/appcloud-frozen-venv`。制品与源码逐字节核验记录：`dwy-auth-artifacts/wheel-sources.json`；认证、EAPI、同步合计 59 个源码文件。临时验收产物不随仓库分发。

三个单应用分别逐字节核对 95、88、90 个已安装 Python 文件。日志位于本次本地临时目录的 `dwy-auth-artifacts/standalone-adbox-smoke.log`、`dwy-auth-artifacts/standalone-quadrant-smoke.log`、`dwy-auth-artifacts/standalone-rightflow-smoke.log`。ADBox 单应用安装包含邮件依赖，另外两产品未安装 Resend。

## 本地使用

按业务仓库 app-cloud 的 `backend/README.md` 先准备固定共享产物，再执行预览构建入口、`uv lock` 更新本机产物摘要和冻结安装。预览 wheel 位于业务仓库的 `.private-packages/auth-runtime-preview`，不覆盖原 `0.4.1` 缓存。当前同版本号仅供本地开发，不等于已发布版本。

配置参考业务仓库 app-cloud 的 `backend/.env.example`。先在开发数据库显式迁移，再启动服务，按 README 的双终端步骤体验真实邮箱闭环。应用接口示例：`http://127.0.0.1:8000/adbox/api/v1/auth/email/code`、`http://127.0.0.1:8000/adbox/api/v1/auth/login`。

## 尚未验收

未运行真实 PostgreSQL 的并发/锁行为、真实邮件投递、真实 Google 账户交互、Apple 购买、Docker 部署或客户端端到端流程。本机无可用 PostgreSQL，Docker daemon 未启动。SQLite、受控 Provider 和安装包测试不能替代这些结果。ADBox 的登录页面、账户切换与离线同步客户端接入属于后续客户端工作。
