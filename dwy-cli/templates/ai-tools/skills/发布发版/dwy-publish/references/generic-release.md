# 通用发布流程（兜底）

适用：不属于前端 / 后端 / Android / iOS / 鸿蒙 五类的发布——CLI 二进制、Docker 镜像、纯 PyPI / npm 库、其他对外包或环境。dwy-shared 自身的 eui / ekit / eapi / cli 走这条。

## 版本（通用步，固化）

- 走 `../dwy-semver` 决策 + bump.py；按 `version-sync.md` 同步工程实际维护的版本来源。
- 发布新代码必须先完成入口规定的版本、changelog 和 tag 闸门；仅重发或回滚相同已记录产物可复用原版本。

## build / publish（项目步，不写死命令）

命令来自缓存（build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`package.json` scripts、`pyproject.toml`、`Makefile`、发布脚本、CI workflow
- 探测不到→问用户→缓存

按缓存 method 分流：
- `github-action-oidc` → **PyPI/npm 首选**，引 `../dwy-github-action-publish`（OIDC + Trusted Publisher）
- `github-action` → Cython wheel / Electron / 镜像，引 `../dwy-github-action-publish`
- 其他渠道 → 遵循项目已有发布配置和授权；PyPI / npm 发布必须走 GitHub Actions OIDC。

**PyPI/npm 未配置 GA 时按 `publish-config.md` 主动推荐 OIDC。**

## changelog / tag / 安全检查 / 监控

- changelog → `changelog.md`（使用该工程既有路径和格式）
- tag → `git-tag.md`（每次 bump 必打；版本串与 changelog 标题一致；monorepo 例：`@dwydev/eui@2.2.3`、`create-dwy@0.16.1`）
- 安全检查 → `../dwy-sdk-spec`（对外包必查泄露/产物）
- 监控 + verify → `monitor-notify.md`（包仓库版本查询 / GitHub Release）
