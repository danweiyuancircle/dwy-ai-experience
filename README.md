# dwy-ai-experience

团队共享基础库与开发工具 monorepo，按 CLI、后端、前端网页和 Apple 客户端四类组织。

[English](README.en.md) · [文档索引](docs/README.md) · [源码与包分发](docs/private-distribution.md)

## 目录与包

| 路径 | 包 / 用途 |
| --- | --- |
| `dwy-cli/` | `create-dwy`：CLI、项目脚手架和 AI 配置同步 |
| `dwy-cli/templates/ai-tools/` | 分发用 skills、rules、hooks 与 hook 清单 |
| `dwy-cli/templates/project/` | 项目脚手架模板 |
| `backend/src/dwyeapi/` | `dwyeapi`：FastAPI 基础设施 |
| `backend/packages/device-fingerprint/` | `dwy-device-fingerprint`：独立设备指纹包 |
| `backend/packages/app-auth/` | `dwy-app-auth`：应用认证与独立管理员会话 |
| `frontend/eui/` | `@dwydev/eui`：Vue 组件库 |
| `frontend/ekit/` | `@dwydev/ekit`：前端工具库 |
| `frontend/admin-shell/` | `@dwydev/admin-kit`：管理端基础框架 |
| `frontend/auth-web/` | `@dwydev/auth-web`：网页认证组件与 Cookie 会话 |
| `frontend/playground/` | 文档与组件演示站 |
| `ios/` | AppleAppKit：iOS/macOS 框架、客户端认证、测试与模板 |
| `ci/`、`scripts/`、`.github/` | 跨包验证与私有构建发布工具 |

根 `Package.swift` 是远程 SwiftPM 入口，源码和测试位于 `ios/`。根 `package.json`、`pnpm-workspace.yaml`、`pnpm-lock.yaml` 统一管理 CLI 与前端；Python 使用 uv 独立管理。

根 `.claude/`、`.agents/` 是开发本仓库时使用的配置，与 CLI 分发模板分开。

## 本地开发

使用 `.node-version` 指定的 Node 和根 `package.json` 指定的 pnpm。以下命令从仓库根执行：

```bash
pnpm install --frozen-lockfile
uv sync --project ci --frozen

pnpm build:frontend
pnpm --dir frontend/auth-web build
pnpm --dir frontend/playground dev
node dwy-cli/bin/index.js --help
```

Python 锁定开发环境统一位于 `ci/`，其中引用本仓库的 EAPI、应用认证和设备指纹源码。

## 验证

```bash
uv run --project ci --frozen pytest backend/tests backend/packages/app-auth/tests scripts/tests -q -o asyncio_mode=auto
pnpm --dir frontend/eui test
pnpm --dir frontend/ekit test
pnpm --dir frontend/admin-shell test
pnpm --dir frontend/auth-web test
pnpm --dir dwy-cli test
swift test
```

Apple 验证需要完整 Xcode 环境。本机使用 Node 26 时，如 Vitest/jsdom 受实验性 Web Storage 影响，可按 [docs/private-distribution.md](docs/private-distribution.md) 局部设置测试环境。

## 接入与分发

- 认证总览：[docs/auth.md](docs/auth.md)。
- EUI 接入与设计规范、Tasks 接入等：[docs/README.md](docs/README.md)。
- Apple 框架与示例：[ios/README.md](ios/README.md)。
- 私有源码与公开包安装：[docs/private-distribution.md](docs/private-distribution.md)。

GitHub 源码保持私有，npm/PyPI 包公开发布，允许任何人安装使用。按包标签触发 `.github/workflows/publish-*.yml`，发布使用 OIDC；`dwy upgrade` 从 npm 更新正式版。CLI 默认读取包内模板，无需源码仓库权限。SwiftPM 继续使用私有 Git 仓库的语义化标签，跨包 CI 和可选 GitHub 快照保留在 `.github/workflows/private-release.yml`。

历史迁移来源、发布与消费者验收证据保留在 [docs/archive/README.md](docs/archive/README.md)，不作为当前接入说明。
