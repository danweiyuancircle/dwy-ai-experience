---
name: dwy-fullstack-scaffold
description: "按 quant-cloud monorepo 架构生成 Web 全栈项目骨架。触发条件：用户说'创建新项目'、'搭骨架'、'新建全栈项目'、'按 quant-cloud 架构创建'、'全栈脚手架'、'scaffold'、'新项目按这个架构'、'开新项目'时。"
---

# dwy-fullstack-scaffold

按照 quant-cloud(/Users/chances/WebstormProjects/ai-quant/quant-cloud/) 的 monorepo 架构生成全栈项目骨架。

## 触发后该做什么(决策树)

```
用户说 "创建新项目 xxx" / "搭骨架"
    ↓
1. 用 AskUserQuestion 收集 5 个关键参数:
   - project_name (kebab-case, 用作目录名 + Docker 服务名)
   - target_dir (默认 /Users/chances/WebstormProjects/<project_name>)
   - scope_prefix (业务包前缀, 默认 'app', 也可填 'quant' / 'foo' 等)
   - initial_domain (示例业务域, 默认 'core', 用户可填 'order' / 'user' 等)
   - include_frontend (默认 true; false 则只生成 backend + 根级)
    ↓
2. 检查 target_dir 不存在或为空。如已存在且非空, AskUserQuestion 确认是否清理。
    ↓
3. 调用 scripts/scaffold.py 生成全部文件:
     uv run python /Users/chances/.claude/skills/dwy-fullstack-scaffold/scripts/scaffold.py \
       --project-name <name> \
       --target-dir <dir> \
       --scope-prefix <prefix> \
       --initial-domain <domain> \
       --include-frontend <true|false>
    ↓
4. 生成完成后自动执行(脚本内做):
   - cd <target_dir>/backend && uv sync --dev
   - cd <target_dir>/frontend && pnpm install (如开 frontend)
    ↓
5. Health check (脚本内做, 临时端口避免冲突):
   - 启 backend: uv run uvicorn app.main:app --port <free_port_be>
   - curl http://127.0.0.1:<free_port_be>/api/health 期望 {"status":"ok"}
   - 启 frontend: pnpm --filter web dev --port <free_port_fe>
   - curl http://127.0.0.1:<free_port_fe>/ 期望 200
   - 全部 kill 干净
    ↓
6. 报告结果 + 下一步指引
```

## 生成的目录结构

```
<project_name>/
├── CLAUDE.md                        # 项目级总入口(融入 quant-cloud 关键约束)
├── dev.sh                           # 一键启动: 杀端口 + Docker + backend + frontend
├── docker-compose.dev.yml           # PG + Redis 基础设施(端口前缀 2xxxx 避冲突)
├── docker-compose.prod.yml          # 生产:三服务硬资源限制 + Redis 双持久化 + 日志轮转
├── deploy/                          # 部署脚本占位
├── docs/                            # 设计文档占位
├── .env.example
├── .gitignore
├── backend/
│   ├── CLAUDE.md                    # 后端约束(分层/Provider/异常/eapi 优先使用等)
│   ├── pyproject.toml               # 单一版本中心 + uv workspace + 双 index(aliyun + pypi)
│   ├── Dockerfile.dev
│   ├── alembic.ini                  # 数据库迁移
│   ├── alembic/env.py
│   ├── src/app/                     # 装配层
│   │   ├── __init__.py              # __version__
│   │   ├── main.py                  # FastAPI lifespan + 装载 packages
│   │   ├── config.py                # eapi BaseSettings 嵌套分组
│   │   ├── exceptions.py
│   │   ├── factories.py             # Provider 工厂(配置驱动切换实现)
│   │   ├── middleware/__init__.py
│   │   └── infra/__init__.py
│   ├── packages/
│   │   ├── dwy-shared/              # 跨项目可复用 kernel
│   │   │   ├── pyproject.toml
│   │   │   └── src/dwy_shared/__init__.py
│   │   └── <scope_prefix>-<initial_domain>/   # 业务包雏形
│   │       ├── pyproject.toml
│   │       └── src/<scope_prefix>_<initial_domain>/
│   │           ├── __init__.py      # register(app) 装载入口
│   │           ├── router.py        # /api/health endpoint
│   │           ├── service.py
│   │           ├── schemas.py
│   │           ├── models.py
│   │           └── protocols.py     # Provider 协议定义
│   └── tests/
│       └── conftest.py
└── frontend/
    ├── CLAUDE.md                    # 前端约束(eui 优先 / pnpm catalog / features 域分包)
    ├── package.json
    ├── pnpm-workspace.yaml          # catalog: 第三方依赖版本统一管理
    ├── tsconfig.base.json
    ├── Dockerfile
    ├── apps/
    │   └── web/
    │       ├── package.json
    │       ├── vite.config.ts
    │       ├── tsconfig.json
    │       ├── index.html
    │       └── src/
    │           ├── main.ts
    │           ├── App.vue          # 起始页含 "Welcome <project_name>" + /api/health 探活
    │           ├── index.css
    │           ├── api/client.ts
    │           ├── router/index.ts
    │           ├── stores/.gitkeep
    │           ├── types/.gitkeep
    │           └── features/<initial_domain>/.gitkeep
    └── packages/
        ├── core/                    # 横切核心(如全局 logger / 类型)
        │   ├── package.json
        │   └── src/index.ts
        ├── ui/                      # 共享 UI 组件包(可选挂载 @dwydev/eui 默认)
        │   ├── package.json
        │   └── src/index.ts
        └── features/
            └── <initial_domain>/
                ├── package.json
                └── src/index.ts
```

## 关键模式(由模板严格保留)

参考 references/architecture.md 的详细说明。要点:

1. **单一版本中心**:backend `pyproject.toml` 集中管理所有外部依赖版本号; frontend `pnpm-workspace.yaml` 的 catalog 集中管理 npm 依赖版本。子包 pyproject/package.json 只写包名,不写版本。
2. **装配层**:`backend/src/app/main.py` 只做"装配",装载 `packages/` 内 `register(app)` 函数。业务逻辑严禁出现在装配层。
3. **域分包**:每个业务 package 内按域(domain)子目录,域内再分 router/service/schemas/models/protocols 五件套。
4. **Provider 模式**:外部服务(数据库 / Redis / SMS / OSS / 第三方 API) 抽象为 Protocol; `factories.py` 按 settings 选具体实现。改实现不改业务代码。
5. **dwy- vs 业务-前缀**:`packages/dwy-*` 是跨项目可复用 kernel; `packages/<scope>-*` 是项目业务专属。
6. **dwyeapi 优先**:后端基础设施(配置 / 异常 / 健康检查 / 缓存 / 任务)先用 dwyeapi,不重复实现。
7. **端口前缀隔离**:每个项目用 1xxxx / 2xxxx / 3xxxx 万位前缀,避免与其他项目冲突。Skill 默认用 2xxxx。
8. **eui / ekit 默认**:前端 catalog 默认含 `@dwydev/eui` + `@dwydev/ekit`(项目可去掉)。

## 用户参数收集

调用脚本前 **必须** 用 AskUserQuestion 收集 5 个参数。提供合理默认值:

| 参数 | 含义 | 默认 | 示例 |
|------|------|------|------|
| project_name | kebab-case 项目名 | (无默认,必问) | `my-app` / `quant-admin` |
| target_dir | 目标父目录 | `/Users/chances/WebstormProjects/<project_name>` | 同上 |
| scope_prefix | 业务包前缀 | `app` | `quant`, `foo` |
| initial_domain | 初始示例业务域 | `core` | `order`, `user`, `factor` |
| include_frontend | 是否生成 frontend | `true` | `true` / `false` |

**target_dir 检查**:已存在且非空 → 用 AskUserQuestion 让用户确认"清理后重建"或"换个目录"或"放弃"。

## 不要做的事

- **不要**改 `templates/` 里的内容(那是 skill 资产,改了影响后续生成)。如要扩展架构,在 SKILL.md 添加描述、补充模板文件,不要 in-place 修改。
- **不要**生成业务代码(订单、用户管理等)。skill 只产出"骨架 + 1 个示意 endpoint"。业务代码由 AI 后续按 CLAUDE.md 引导补。
- **不要**跳过 health check。生成完成必须验证 backend `/api/health` + frontend 首页 200。失败要报告原因,不能假装成功。
- **不要**生成 `.git/`(让用户自己 `git init`)。
- **不要**安装 `@dwydev/eui` 之外的额外 UI 库(如 Element Plus / Ant Design Vue)。

## 生成完成后的报告模板

```markdown
✅ 项目 <project_name> 骨架已生成

📁 路径: <target_dir>

📦 已安装依赖:
  - backend (uv sync --dev): <duration> s
  - frontend (pnpm install): <duration> s   [仅当 include_frontend=true]

✅ Health check:
  - GET http://127.0.0.1:<be_port>/api/health → 200 {"status":"ok"}
  - GET http://127.0.0.1:<fe_port>/ → 200          [仅当 include_frontend=true]

🚀 下一步:
  cd <target_dir>
  ./dev.sh

🛠 业务开发起点:
  - backend: backend/src/app/main.py 装载 packages/<scope>-<domain>/
    -> 加新业务: 复制 <scope>-<domain>/ 整个目录,改名后在 main.py 装载
  - frontend: frontend/apps/web/src/features/<domain>/ + packages/features/<domain>/
    -> 加新功能: 在 features/ 下加目录,在 router/index.ts 注册路由

📋 待办(skill 没替你做):
  - git init && git add . && git commit -m "chore: initial scaffold from dwy-fullstack-scaffold"
  - 在 .env 中填真实 DATABASE_URL / REDIS_URL / SECRET_KEY (默认值仅适合本地)
  - 按需调整 packages/dwy-shared/ 的依赖范围
  - 按需启用 alembic: cd backend && uv run alembic init -t async alembic (skill 已留 alembic.ini, env.py 雏形)
```

## 失败排错

生成或 health check 失败时,先看脚本输出最后 50 行(脚本会打印每一步的命令 + stderr)。常见失败:

| 症状 | 原因 | 解决 |
|------|------|------|
| `uv sync` 报 dwyeapi 找不到 | 默认 aliyun 镜像可能没同步 | pyproject 里 dwyeapi 已声明 `index = "pypi-org"`,确保 uv >=0.4 |
| `pnpm install` 报 catalog 找不到 | pnpm <8.x 不支持 catalog | 升 pnpm: `npm i -g pnpm@latest` |
| backend health check 端口冲突 | 别的进程占了 28001 | 脚本会自动找 free port,不应发生; 看脚本日志 |
| `vite` 启不来 | apps/web 缺 `@vitejs/plugin-vue` | catalog 已含,确认 pnpm install 没出错 |
| `register()` 找不到 | scope_prefix 含特殊字符 | 用 lowercase + 字母数字下划线,kebab-case |

## 后续扩展

加新业务 package(例如订单系统 `quant-order`):

1. 复制 `backend/packages/<scope>-<initial_domain>/` 整体到 `<scope>-<new_domain>/`
2. 改 `pyproject.toml` 的 `name` 字段
3. 改 `src/<scope>_<new_domain>/__init__.py` 的 `register()` 函数名(可选,主要是 import 路径)
4. 改 `src/app/main.py` 加 `from <scope>_<new_domain> import register as register_<new_domain>`
5. lifespan 里调 `register_<new_domain>(app)`

加新前端 feature:

1. 在 `frontend/packages/features/` 复制示例 feature 整体改名
2. 在 `frontend/apps/web/src/features/` 加同名目录(页面层)
3. `apps/web/src/router/index.ts` 注册路由
