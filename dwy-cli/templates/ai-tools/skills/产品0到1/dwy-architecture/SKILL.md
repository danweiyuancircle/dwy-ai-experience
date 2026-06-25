---
name: dwy-architecture
description: "【dwy·技术架构】产品 0 到 1 设计与架构阶段。触发场景：用户说『设计架构 / 出技术方案 / 设计库表 / 定接口契约 / 技术架构 / architecture』，要在开发前定下技术架构、数据库设计和接口契约时。按四层架构（Assembly/Features/BizFoundation/Foundation）+ 统一选型（Python+FastAPI、Vue+Vite）产出。"
---

## 职责（单一）
按项目 rules + 下方架构约束，产出技术架构 + 数据库库表设计 + 接口契约。

## 输入（从哪读）
- state.json 的 `confirmed.prd`、`confirmed.tasks`、`confirmed.prototype`
- `.dwy/prod/[项目]/02-需求规划/PRD.md`、`开发任务拆解.md`
- 项目 `.claude/rules/` 下的技术栈与编码规则

## 架构约束（硬）

项目已有 `.claude/rules/` 时**以项目 rules 为准**；项目无明确规定时按本节统一缺省。

### 技术选型（缺省基线，写在架构选项之上）

以下为默认选型基线，**先按此基线落地**；结合上下文（PRD / 选型 / 项目 rules）判断**基线不合适时，必须用 `AskUserQuestion` 跟用户确认后才换**，禁止默默偏离基线、也禁止默默换栈。

- **后端统一 Python + FastAPI**（异步、Pydantic v2、SQLAlchemy 2.0 风格，与 `dwyeapi` 生态对齐）
  - **Python 虚拟环境用 `uv` 管理**（venv + 依赖 + 运行）
  - **DB 迁移用 Alembic**（与 SQLAlchemy 2.0 配套）
  - **配置 / settings 用 pydantic-settings**（与 `dwyeapi` config 对齐）
  - **认证用 JWT**（与 `dwyeapi` security 的 create_token/decode_token + bcrypt 对齐）
- **后端有数据库时**：
  - **关系型数据库用 PostgreSQL**（连接串如 `postgresql+asyncpg://user:pass@localhost:5432/mydb`）
  - **内存数据库 / 缓存用 Redis**（`redis://localhost:6379/0`）
  - **用 Docker 部署**（后端 + Postgres + Redis 编排到 `docker-compose.yml`）
  - **反向代理 / 入口网关用 Nginx**
- **前端 Vue 用 Vite + TailwindCSS + TypeScript**（`@dwydev/eui` + `@dwydev/ekit` 可选用，不强制）
  - **包管理器用 pnpm**（与本 monorepo 一致）
  - **状态管理用 Pinia**
  - **HTTP 客户端用 axios**（或 `@dwydev/ekit` 的 request）
  - **E2E 测试用 Playwright**（单测 Vitest 为项目默认）
- **CI/CD 走 GitHub Actions + OIDC**（发布鉴权用 OIDC，禁长期静态凭据）
- **基线不适用就先确认**：任一项基线与上下文冲突（如纯前端无需 Docker/DB、要换其他 DB/MQ/中间件、不能用某项）→ 先 `AskUserQuestion` 跟用户确认，确认后在架构文档写明偏离基线的理由

### 四层架构（依赖严格单向向下：Assembly → Features → BizFoundation → Foundation）

| 层 | 职责 | 后端示例 | 前端示例 |
|---|---|---|---|
| **装配层 (Assembly)** | 实例化 / 依赖注入 / 路由挂载 / 生命周期，**零业务逻辑** | `src/app/`（main.py 装 Provider/Hook、factories） | `apps/web`（路由、stores、main.ts） |
| **Features (业务功能层)** | 各业务域领域逻辑，域内 router+service+schema+model **聚在同一目录** | `<域>/`（如 `factor/`、`plan/`、`quota/`） | `features/*`（如 auth、settings） |
| **业务基础层 (BizFoundation)** | 业务相关但跨业务域复用：鉴权、领域协议/Provider、领域设施 | `auth`、各包 `protocols.py`/`providers` | 跨域复用的业务 composable/store |
| **业务无关层 (Foundation)** | 与业务完全无关的 kernel | `shared`（DB/Redis/签名/中间件） | `core`（httpClient/格式化/常量） |

### 三条铁律
- **依赖单向向下，绝不反向**：下层禁止 import 上层；Foundation 禁止 import 任何业务包；跨业务域**不直接互 import**，靠装配层用 Protocol/Hook 桥接。
- **业务内聚**：一个业务域 = 一个目录，域内 router/service/schema/model 聚在一起。✅ `factor/`（含 router+service+validators）；❌ 顶层 `routers/`+`services/`+`models/` 三个大锅各塞所有域。
- **装配层是唯一能 import 具体实现的地方**：业务代码只通过 `get_xxx_provider()` 取实例，换实现不改业务代码。

## 实现
[自写型]
1. 读项目 `.claude/rules/`，结合上方架构约束产出架构（项目 rules 优先，本约束兜底）
2. 技术架构：**先按四层归位模块、按业务域聚目录**，再写分层/模块边界/选型理由；选型不确定处走 `AskUserQuestion`
3. **判有无后端**（读选型/PRD：有 API / 持久化 / 账户体系 → 有后端）：
   - **有后端** → 必出数据库设计，且**建模到位**：库表清单 / 字段(类型·约束·默认·可空) / 主外键关系 / 索引 / 必要的范式或反范式说明，与接口契约 schema 对齐
   - **纯前端**（无后端）→ 跳过数据库设计，在 `技术架构.md` 注明「无后端，不涉及库表」
4. 接口契约：路由、请求/响应 schema（遵循项目响应格式约定）
5. **走 rules + 约束土建**，不引入约束外的技术栈

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/04-架构设计/技术架构.md`、`接口契约.md`，**有后端时**加 `数据库设计.md`
- 固定章节：
  - 技术架构.md：**四层划分 + 各业务域目录结构** / 模块边界 / 技术选型（按缺省基线写明 Python+FastAPI+uv+Alembic+pydantic-settings+JWT、前端 Vue+Vite+TS+Tailwind+pnpm+Pinia+axios+Playwright、CI/CD GitHub Actions OIDC；有 DB 写明 PostgreSQL+Redis+Docker+Nginx；偏离基线处写明原因）/ 选型不明或偏离基线处的 AskUserQuestion 确认记录 / 有无后端结论
  - 数据库设计.md（**有后端必出**）：库表清单 / 字段定义(类型·约束·默认·可空) / 主外键关系与索引 / 与接口契约对齐
  - 接口契约.md：接口清单 / 请求响应 schema / 错误码
- 回写 state.json：`confirmed.architecture`
