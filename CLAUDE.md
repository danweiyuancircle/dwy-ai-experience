# dwy-shared

共享基础包 monorepo，包含前端、后端、CLI 工具三部分。

## 结构

```
frontend/       # 前端共享包（npm 发布）
  eui/          # @danweiyuan/eui — Vue 3 组件库（89 组件）
  core/         # @danweiyuan/core — 工具库（request/storage/validators/hooks/date）

backend/        # 后端共享包（PyPI 发布）
                # danweiyuan-base — FastAPI 基础设施

claude-cli/     # CLI 工具（npm 发布）
                # create-dwy — 项目脚手架 + Claude 配置同步
```

## 发布命令

```bash
# 前端
pnpm build:eui && pnpm publish:eui
pnpm build:core && pnpm publish:core

# 后端
pnpm publish:backend

# CLI
pnpm publish:cli
```

## 开发

```bash
pnpm install                    # 安装前端依赖
cd backend && uv venv && uv pip install -e ".[dev]"  # 安装后端依赖
```
