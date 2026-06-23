# 通用发布流程（兜底）

适用：不属于前端 / 后端 / Android / iOS / 鸿蒙 五类的发布——CLI 二进制、Docker 镜像、纯 PyPI / npm 库、其他对外包或环境。dwy-shared 自身的 eui / ekit / eapi / cli 走这条。

## 版本（通用步，固化）

- 走 `../dwy-semver` 决策 + bump.py；多文件同步见 `version-sync.md`（Python 同步 `pyproject.toml` + `__init__.py`，Node 同步 `package.json`）。
- 纯重发、仅重跑 workflow、仅回滚已有构建时可不 bump。

## build / publish（项目步，不写死命令）

命令来自缓存（build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`package.json` scripts、`pyproject.toml`、`Makefile`、发布脚本、CI workflow
- 探测不到→问用户→缓存

按缓存 method 分流：
- `github-action-oidc` → **PyPI/npm 首选**，引 `../dwy-github-action-publish`（OIDC + Trusted Publisher）
- `github-action` → Cython wheel / Electron / 镜像，引 `../dwy-github-action-publish`
- `local` → 缓存的本地发包命令（`uv publish` / `pnpm publish` 等）

**PyPI/npm 未配置 GA 时按 `publish-config.md` 主动推荐 OIDC。**

## changelog / 安全检查 / 监控

- changelog → `changelog.md`（单包仓库根目录一份；monorepo 按包目录过滤）
- 安全检查 → `../dwy-sdk-spec`（对外包必查泄露/产物）
- 监控 + verify → `monitor-notify.md`（包仓库版本查询 / GitHub Release）
