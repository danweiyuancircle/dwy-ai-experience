# 后端部署流程

适用：后端服务、API、容器或镜像、线上后端环境。

## 版本（通用步，固化）

- 走 `../dwy-semver` 决策 + bump.py；多文件同步见 `version-sync.md`（Python 须同步 `pyproject.toml` 的 `version` 和包 `__init__.py` 的 `__version__`）。
- 纯重发、仅重跑 workflow、仅补环境配置、仅回滚已有构建时可不 bump。

## build / deploy（项目步，不写死命令）

命令来自缓存（build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`Dockerfile`、`docker-compose`、部署脚本、`Makefile`、`pyproject.toml`、CI workflow
- 探测不到→问用户→缓存

按缓存 method 分流：
- `github-action` → 引 `../dwy-github-action-publish`（CI 推荐 OIDC，先过通用检查）
- `local` → 缓存的本地构建/部署命令（打镜像 / 部署脚本）

## changelog / 监控

- changelog → `changelog.md`（写 `backend/CHANGELOG.md`）
- 监控 + verify → `monitor-notify.md`（后端信号：健康检查 / 版本接口 / 运行日志 / 镜像 tag）
