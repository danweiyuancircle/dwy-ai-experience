# 发布方式缓存 + 命令探测

发布方式与 build/publish 命令**因项目而异，不写死**。按应用目录探测 → 问 → 缓存复用。

## 缓存机制

- 缓存文件：`<project_root>/.dwy/publish/config.json`，读写走 `scripts/release_config.sh`。
- key = **相对项目根的相对目录**（如 `ios`、`apps/electron`，根用 `.`）。
- `.dwy/` 是本机判断缓存，**提醒用户加进 `.gitignore`**，不入版本库。

## 读写流程

1. 确定本次要发的**应用目录**（相对路径）。
2. `release_config.sh get <root> <rel_dir>`：
   - 命中且 `configured=true` → 用缓存的 method + build_cmd/publish_cmd/verify_cmd
   - 比对 `cmd_source`：若项目里对应命令源（package.json scripts / Fastfile / workflow 等）已变 → 重新探测+问用户+更新缓存
   - 未命中（首次进入该目录）→ 走第 3 步
3. 首次配置：
   - 探测真实命令（见下方探测线索）
   - AskUserQuestion 问发布方式（见下方各平台候选）
   - 检查对应配置就绪（GA workflow 是否存在 / TestFlight 凭据线索 / maven·pod publish 配置）
   - `release_config.sh set <root> <rel_dir> <platform> <method> <channel> <configured> [build_cmd] [publish_cmd] [verify_cmd] [cmd_source]`
   - 提醒把 `.dwy/` 加进 `.gitignore`
4. 目录与缓存对不上（仓库结构变了）：先 AI 自助判断目录是否仍正确，判不准再问用户，必要时 `reset` 重建。

全程 AI 自动跑，仅探测不到 / 命令歧义 / 配置缺失时才问用户。

## build/publish 命令探测线索（不写死，按项目找）

| 平台 | 去哪找真实命令 |
|------|---------------|
| 前端 | `package.json` scripts（build/deploy）、`vite.config.*`、`.github/workflows/`、`Makefile` |
| 后端 | `Dockerfile`、`docker-compose`、部署脚本、`Makefile`、`pyproject.toml`、`.github/workflows/` |
| iOS | `fastlane/Fastfile`、`*.xcodeproj` / `*.xcworkspace`、`Makefile`、CI workflow、`package.json` scripts |
| Android | `build.gradle(.kts)` task、`gradlew`、`fastlane/`、CI workflow |
| 鸿蒙 | `build-profile.json5`、ohpm 脚本、DevEco 构建配置、CI workflow |
| 通用包 | `package.json` scripts、`pyproject.toml`、`Makefile`、发布脚本、`.github/workflows/` |

探测到多个候选时问用户选；探测不到时问用户给命令。命令存进缓存的 `build_cmd`/`publish_cmd`/`verify_cmd`。

## 各平台发布方式候选（AskUserQuestion）

先按平台 + 产物形态（应用包 vs SDK）裁剪候选，推荐项标注：

| platform / 产物 | method 候选 |
|------|------|
| ios 应用包（ipa） | `testflight`(推荐) / `github-action` / `local` / `manual` |
| ios SDK（framework/xcframework） | `cocoapods` / `spm` / `github-action` / `local` |
| android 应用包（apk/aab） | `github-action`(推荐) / `local` |
| android SDK（aar） | `maven`(推荐) / `github-action` / `local` |
| harmony（har / har app） | `ohpm`(推荐) / `github-action` / `local` |
| frontend | `github-action`(CI，推荐 OIDC) / `local` |
| backend | `github-action`(CI，推荐 OIDC) / `local` |
| generic — PyPI/npm | `github-action-oidc`(**推荐**，无静态凭据、符合团队准则) / `local` |
| generic — Cython wheel | `github-action`(cibuildwheel) / `local` |
| generic — Electron | `github-action`(多平台 runner) / `local` |
| generic — Docker/二进制 | `github-action` / `local` |

## PyPI / npm 首次配置：主动推荐 GitHub Action OIDC

PyPI / npm 且未配置 GA 时，**主动推荐 `github-action-oidc`**（OIDC Trusted Publishing，无长期静态凭据）：

- 给 workflow 模板：见 `../dwy-github-action-publish`（Python wheel / 纯包 OIDC）。
- 给 Trusted Publisher 网页配置步骤：PyPI/npmjs 后台绑定 repo + workflow 文件名 + environment。
- 用户仍可选 `local`（`uv publish` / `pnpm publish` 等），按其选择缓存。
