# 前端部署流程

适用：站点、SPA、SSR、前端容器镜像或线上前端环境。

## 版本（通用步，固化）

- 走 `../dwy-semver` 决策 + bump.py；多文件同步见 `version-sync.md`（前端改 `package.json` 的 `version`）。
- 纯重发、仅重跑 workflow、仅回滚已有构建时可不 bump。

## build / deploy（项目步，不写死命令）

命令来自缓存（build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`package.json` scripts（build/deploy）、`vite.config.*`、`Dockerfile`、`Makefile`、CI workflow
- 探测不到→问用户→缓存

按缓存 method 分流：
- `github-action` → 引 `../dwy-github-action-publish`（CI 推荐 OIDC，先过通用检查）
- `local` → 缓存的本地构建/部署命令（推镜像 / 传 CDN·OSS / 部署脚本）

## changelog / 监控

- changelog → `changelog.md`（写 `frontend/CHANGELOG.md`）
- 监控 + verify → `monitor-notify.md`（前端信号：页面访问 / 版本接口 / 产物 hash / CDN 刷新）
