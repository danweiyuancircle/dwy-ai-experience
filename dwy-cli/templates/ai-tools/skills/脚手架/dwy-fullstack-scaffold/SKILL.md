---
name: dwy-fullstack-scaffold
description: "调用 dwy create CLI 生成全栈 Vue 3 + FastAPI monorepo 骨架，并完成 post-create 安装 + health check 编排。触发条件：用户说'创建新项目'、'搭骨架'、'新建全栈项目'、'fullstack monorepo'、'全栈脚手架'、'scaffold'、'开新项目'时。"
---

# dwy-fullstack-scaffold

调用 `dwy create` CLI 选 `fullstack-monorepo` 模板生成全栈 monorepo 骨架，然后用 Bash 编排 post-action（依赖安装 + health check）。

## 触发后该做什么(决策树)

```
用户说 "创建新项目 xxx" / "搭骨架"
    ↓
1. 用 AskUserQuestion 收集 5 个关键参数（如用户已说明部分，直接用，缺什么问什么）:
   - project_name (kebab-case, 用作目录名 + Docker DB 名)
   - target_parent_dir (默认 /Users/chances/WebstormProjects)
   - scope_prefix (业务包前缀, 默认 'app')
   - initial_domain (示例业务域, 默认 'core')
   - include_frontend (默认 true)
   - port_prefix (端口前缀数字, 1-9, 默认 '2')
    ↓
2. 检查 <target_parent_dir>/<project_name> 不存在或为空。已存在且非空 → AskUserQuestion 确认是否清理。
    ↓
3. 调用 dwy create（在 target_parent_dir 下执行）:
     cd <target_parent_dir>
     dwy create <project_name>
   交互时回答:
     - 项目模板: fullstack-monorepo
     - 业务包前缀: <scope_prefix>
     - 初始业务域: <initial_domain>
     - 是否生成 frontend: <include_frontend>
     - 端口前缀数字: <port_prefix>

   或者用环境变量 / 配置非交互模式（如果 dwy CLI 支持）。当前最稳的做法是用 expect 模拟交互，或者让用户自己跑 dwy create，本 skill 负责后续编排。

   **推荐做法**：让用户在终端跑 `dwy create <project_name>` 自己回答交互（每次脚手架问题需要人 review），然后 skill 介入做 post-action。
    ↓
4. 安装依赖（在 <target_parent_dir>/<project_name> 下）:
   - cp backend/.env.example backend/.env (如未存在)
   - cp frontend/.env.example frontend/.env (仅当 include_frontend=true 且未存在)
   - cd backend && uv sync --dev
   - cd frontend && pnpm install (仅当 include_frontend=true)
    ↓
5. Health check（用临时端口避免冲突）:
   - free_port_be=$(python3 -c "import socket;s=socket.socket();s.bind(('',0));print(s.getsockname()[1])")
   - 临时启 backend: uv run uvicorn app.main:app --port $free_port_be &
   - 等 1-3 秒，curl http://127.0.0.1:$free_port_be/api/health 期望 {"status":"ok",...}
   - kill backend 进程
   - 如 include_frontend=true:
     - free_port_fe=$(...)
     - pnpm --filter @<project_name>/web dev --port $free_port_fe &
     - 等 3-5 秒，curl http://127.0.0.1:$free_port_fe/ 期望 200
     - kill frontend 进程
    ↓
6. 报告结果 + 下一步指引
```

## 生成的目录结构

`dwy create` 选 `fullstack-monorepo` 模板会生成：

```
<project_name>/
├── CLAUDE.md                            # 项目级总入口
├── scripts/
│   └── dev.sh                           # 一键启动: 杀端口 + Docker + backend + frontend
├── docs/                                # 设计文档占位
├── docker-compose.dev.yml               # dev: PG + Redis(端口前缀 <port_prefix>xxxx)
├── docker-compose.prod.yml              # prod: backend + db + redis(资源限制 + 日志轮转)
├── .gitignore
├── backend/
│   ├── CLAUDE.md                        # 后端约束（域分包 / Provider / dwyeapi 优先）
│   ├── .env.example                     # backend 环境变量样例
│   ├── pyproject.toml                   # uv workspace + 双 index + 版本中心
│   ├── Dockerfile.dev / Dockerfile.prod
│   ├── alembic.ini + alembic/env.py
│   ├── src/app/                         # 装配层
│   │   ├── main.py                      # FastAPI lifespan + register 业务包
│   │   ├── config.py                    # Settings 嵌套配置
│   │   ├── factories.py                 # Provider 工厂占位
│   │   ├── exceptions.py
│   │   ├── middleware/  infra/
│   ├── packages/
│   │   ├── dwy-shared/                  # 跨项目通用 kernel
│   │   └── <scope_prefix>-<initial_domain>/   # 业务包雏形
│   │       └── src/<scope>_<domain>/
│   │           ├── __init__.py          # register(app, *, config) 装载入口
│   │           ├── config.py            # DomainConfig
│   │           ├── router.py            # /api/<domain>/health endpoint
│   │           ├── service.py
│   │           ├── schemas.py
│   │           ├── models.py
│   │           └── protocols.py
│   └── tests/conftest.py
└── frontend/                            # 仅当 include_frontend=true
    ├── CLAUDE.md                        # 前端约束（eui 优先 / catalog / features 域分包）
    ├── .env.example                     # Vite VITE_* 变量样例
    ├── package.json
    ├── pnpm-workspace.yaml              # catalog 统一版本
    ├── tsconfig.base.json
    ├── Dockerfile + nginx.conf
    ├── apps/web/
    │   ├── vite.config.ts               # 端口前缀 + /api proxy
    │   └── src/{main.ts, App.vue, router, api, views, features/, stores/, types/}
    └── packages/
        ├── core/                         # 横切核心
        ├── ui/                           # 项目级共享 UI（基于 @dwydev/eui）
        └── features/<initial_domain>/    # 业务功能包雏形（导出 createFeatureRoutes()）
```

## 关键模式

详细参考生成的项目内 `CLAUDE.md`。要点：

1. **单一版本中心**：backend `pyproject.toml` 集中管理外部依赖版本；frontend `pnpm-workspace.yaml` 的 `catalog:` 集中管理 npm 依赖版本
2. **装配层只装配**：业务逻辑在 `packages/<scope>-<domain>/`，不在 `src/app/`
3. **域分包**：每业务包五件套 router/service/schemas/models/protocols + 一个 config
4. **Provider 模式**：外部服务抽象为 Protocol，`factories.py` 选实现
5. **dwy- vs 业务-前缀**：`packages/dwy-*` 跨项目；`packages/<scope>-*` 项目专属
6. **dwyeapi 优先**：后端基础设施先用 dwyeapi
7. **端口前缀**：`<port_prefix>xxxx`，默认 2（28001/25173/25432/26379）
8. **eui / ekit 默认**：前端 catalog 默认含 `@dwydev/eui` + `@dwydev/ekit`

## 用户参数收集（必做）

调用 `dwy create` 前 **必须** 用 AskUserQuestion 收集 5 个参数（用户已明确给出的省去）：

| 参数 | 含义 | 默认 | 示例 |
|------|------|------|------|
| project_name | kebab-case 项目名 | (无默认,必问) | `my-app` |
| scope_prefix | 业务包前缀 | `app` | `quant`, `foo` |
| initial_domain | 初始示例业务域 | `core` | `order`, `user` |
| include_frontend | 是否生成 frontend | `true` | `true` / `false` |
| port_prefix | 端口万位前缀 (1-9) | `2` | `2`, `3` |

**目录检查**：`<target_parent_dir>/<project_name>` 已存在且非空 → AskUserQuestion 让用户确认"清理后重建"或"换个目录"或"放弃"。

## 不要做的事

- **不要**直接写脚本生成模板。模板由 `dwy create` 渲染，本 skill 只负责参数收集 + post-action 编排
- **不要**修改生成的项目骨架（除非用户要求扩展业务）。生成完后的业务代码由 AI 后续按生成项目里的 `CLAUDE.md` 引导补
- **不要**跳过 health check。失败要报告原因，不能假装成功
- **不要**生成 `.git/`（让用户自己 `git init`）
- **不要**在生成后强行 `git init && commit`（让用户决策）
- **不要**安装 `@dwydev/eui` 之外的额外 UI 库

## 生成完成后的报告模板

```markdown
✅ 项目 <project_name> 骨架已生成

📁 路径: /Users/chances/WebstormProjects/<project_name>

📦 已安装依赖:
  - backend (uv sync --dev): <duration> s
  - frontend (pnpm install): <duration> s    [仅当 include_frontend=true]

✅ Health check:
  - GET http://127.0.0.1:<free_port_be>/api/health → 200 {"status":"ok",...}
  - GET http://127.0.0.1:<free_port_fe>/ → 200           [仅当 include_frontend=true]

🚀 下一步:
  cd /Users/chances/WebstormProjects/<project_name>
  cp backend/.env.example backend/.env       # dev 默认值可直接用,prod 改 DATABASE_URL/SECRET_KEY
  cp frontend/.env.example frontend/.env     # Vite 变量(仅 include_frontend=true 时)
  ./scripts/dev.sh

🛠 业务开发起点:
  - backend: backend/src/app/main.py 装载 packages/<scope>-<domain>/
    → 加新业务: 复制 packages/<scope>-<domain>/ 整体改名 + 在 main.py 装载
  - frontend: frontend/packages/features/<domain>/ + frontend/apps/web/src/features/<domain>/
    → 加新功能: 在 features/ 下加目录，在 router/index.ts 注册路由

📋 待办(skill 没替你做):
  - cd /Users/chances/WebstormProjects/<project_name> && git init && git add . && git commit -m "chore: initial scaffold"
  - 在 .env 中填真实 DATABASE_URL / REDIS_URL / SECRET_KEY (默认值仅适合本地)
  - 按需 alembic init: cd backend && uv run alembic upgrade head
```

## 失败排错

| 症状 | 原因 | 解决 |
|------|------|------|
| `dwy create` 命令找不到 | create-dwy 未安装或不在 PATH | `pnpm i -g create-dwy` 或在 dwy-shared 仓库 `pnpm link --global` |
| `dwy create` 报模板找不到 | 当前版本 CLI 未包含对应模板，或用户本机 install 的版本落后 | 升级 `create-dwy` 到最新版本；确认 `dwy --version` 与线上版本一致后重试 |
| `uv sync` 报 dwyeapi 找不到 | aliyun 镜像未同步 | pyproject 已声明 pypi-org 备 index，确保 uv >=0.4 |
| `pnpm install` 报 catalog 找不到 | pnpm <10 不支持 catalog | 升级: `npm i -g pnpm@latest` |
| backend health check 失败 | DATABASE_URL/SECRET_KEY 用了占位值导致启动报错 | 检查 .env 是否已 cp 自 .env.example；查 uvicorn stderr 输出 |
| frontend health check 失败 | catalog 版本未对齐或 EUI peerDep 缺失 | 看 pnpm install 输出错误，按 catalog 加缺失版本 |
| `register()` 找不到 | scope_prefix 含特殊字符 | scope_prefix 只允许小写字母开头 + 字母数字 |

## 后续扩展

**加新后端业务包**（如 `app-order`）:

1. 复制 `backend/packages/<scope_prefix>-<initial_domain>/` 整体改名 `app-order/`
2. 改 `pyproject.toml` 的 `name` 字段
3. 改 `src/app_order/__init__.py` 的导入路径
4. 改 `src/app/main.py` 加 `from app_order import register as register_order; register_order(app, config=settings.order)`
5. 在 `src/app/config.py` 加 `order: DomainConfig` 字段

**加新前端 feature**（如 `order`）:

1. 复制 `frontend/packages/features/<initial_domain>/` 改名 `frontend/packages/features/order/`
2. 在 `frontend/apps/web/src/router/index.ts` 加 `import { createFeatureRoutes as createOrderRoutes } from '@<project_name>/features-order'` 并装载
3. 在 `frontend/tsconfig.base.json` 加路径别名 `@<project_name>/features-order`
4. 在 `frontend/apps/web/package.json` 加 workspace 依赖 `@<project_name>/features-order: workspace:*`
