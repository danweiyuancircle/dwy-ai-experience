# 私有源码与公开包分发

GitHub 源码仓库 `https://github.com/danweiyuancircle/dwy-ai-experience` 保持私有。npm/PyPI 安装包公开发布，允许任何人下载使用，无需 GitHub 仓库权限。公开包包含运行所需实现与资源；仓库可见性与安装包可见性分开管理。

## 发布入口

| 包 | 目录 | 标签 | GitHub Actions |
| --- | --- | --- | --- |
| `@dwydev/eui` | `frontend/eui/` | `@dwydev/eui@VERSION` | `.github/workflows/publish-eui.yml` |
| `@dwydev/ekit` | `frontend/ekit/` | `@dwydev/ekit@VERSION` | `.github/workflows/publish-ekit.yml` |
| `@dwydev/admin-kit` | `frontend/admin-shell/` | `@dwydev/admin-kit@VERSION` | `.github/workflows/publish-admin.yml` |
| `@dwydev/auth-web` | `frontend/auth-web/` | `@dwydev/auth-web@VERSION` | `.github/workflows/publish-auth-web.yml` |
| `create-dwy` | `dwy-cli/` | `create-dwy@VERSION` | `.github/workflows/publish-cli.yml` |
| `dwyeapi` | `backend/` | `dwyeapi@VERSION` | `.github/workflows/publish-eapi.yml` |
| `dwy-auth` | `backend/packages/auth/` | `dwy-auth@VERSION` | `.github/workflows/publish-auth.yml` |
| `dwy-device-fingerprint` | `backend/packages/device-fingerprint/` | `dwy-device-fingerprint@VERSION` | `.github/workflows/publish-device-fingerprint.yml` |
| `dwy-webhooks` | `backend/packages/webhooks/` | `dwy-webhooks@VERSION` | `.github/workflows/publish-webhooks.yml` |

`VERSION` 必须与对应包元数据一致。正常分支推送只验证代码，不发布 registry 包。修改后需要发布新版本，不能覆盖已经存在的 npm/PyPI 版本，也不重打已交付标签。

所有发布都走 GitHub Actions + OIDC，不使用长期 npm/PyPI token；发布前使用 `scripts/private_release.py check` 验证源码仓库仍为私有。

每个 npm 包需要先完成包初始化，再在 npm 后台配置 Trusted Publisher，绑定本仓库及对应工作流文件；新增 npm 包不能只添加工作流就假设首发授权已经可用。PyPI 项目同样需要配置可信发布者，新项目可配置 Pending Publisher。这些后台绑定需在实际发版前核对，源码配置不能代替后台授权；不以长期发布 token 绕过这些前提。

首次交付按依赖顺序推进：先发布独立的 `dwy-device-fingerprint` 和 `dwy-auth`，再发布提供 `device` / `auth` extra 的 `dwyeapi`，最后发布依赖 EAPI 的 `dwy-webhooks`。前一层实际出现在公共 PyPI 后才能推送下一层的标签。认证核心不依赖 EAPI，`dwyeapi[auth]` 精确依赖认证包；EAPI 邮件适配与旧认证 HTTP 接口仍需配套安装新版 EAPI。前端包先满足 EUI/EKIT 的依赖版本，再发布依赖它们的管理端与网页认证包。

`dwy-auth`、`dwy-device-fingerprint` 和 `dwy-webhooks` 的 PyPI Trusted Publisher 分别绑定上表工作流文件及 GitHub `pypi` environment。已有 `dwyeapi` 继续使用既有可信发布者绑定。发布权限来自 GitHub 的短期 OIDC 身份，仓库和本机均不保存 PyPI 发布 token。

每个 Python 发布工作流在上传前执行 `scripts/check_python_distribution.py`：检查 wheel 命名空间、归档敏感文件和直接源依赖，再在仓库外创建临时环境，从官方 PyPI 解析依赖并安装本轮实际 wheel，使用隔离 Python 验证版本和导入路径。源码测试通过但公开依赖缺失时，发布会在上传前失败。

私有源码仓库可以使用 npm Trusted Publishing，但不会产生公开源码 provenance；不添加强制 provenance 参数。公开 npm 包不设置 `private: true`，scoped 包使用 `publishConfig.access: public`；根工作区仍保留 `private: true`。Python 包不使用禁止上传的 Private classifier。

## 安装与更新

下面命令安装 registry 中已经发布的版本；工作区中的新功能需要完成新版本发布后才会进入这些安装入口。

```bash
pnpm add @dwydev/eui @dwydev/ekit @dwydev/admin-kit @dwydev/auth-web
npm install --global create-dwy
dwy upgrade
python -m pip install 'dwyeapi[auth,device]==0.12.0' 'dwy-webhooks[discord,resend,apple]==0.1.0'
```

`dwy` 默认使用安装包内的 `templates/ai-tools/`，不克隆私有源码仓库。开发者可显式使用 `DWY_TEMPLATE_SOURCE_DIR` 指向本地模板目录；不存在的显式目录会报错。

本地 Web 验证使用 `.node-version` 指定的 Node 22.14.0。本机若使用 Node 26，其原生 Web Storage 可能干扰 Vitest/jsdom，可局部设置 `NODE_OPTIONS=--no-experimental-webstorage` 运行测试。

## SwiftPM 与 GitHub 快照

Apple 消费者继续通过 Xcode/SwiftPM 访问私有 Git 仓库，使用标准语义化版本标签；需要相应仓库读取权限。公开 npm/PyPI 发布不会改变 SwiftPM 的访问方式。

`.github/workflows/private-release.yml` 保留跨包 Web/Python/Swift 验证，并可在语义化标签下生成私有 GitHub Release 快照。快照使用短期 `GITHUB_TOKEN`，包含实际构建产物、`release-manifest.json` 和 `SHA256SUMS`，是补充交付渠道。

历史 `0.4.1` GitHub Release 及其原始哈希清单保留，不能把后续同版本重建产物冒充该历史发布。需要下载历史快照时，可使用 `scripts/private_release.py download`，命令会验证产物大小和哈希；日常 Node/Python 消费直接使用公开 registry。

## 验证边界

本地构建、单测、YAML 检查和安装包 smoke 不代表 npm/PyPI 已经发布成功。正式发布还需核对可信发布者绑定，运行标签工作流，并从公共 registry 安装新版本验收。

真实 Google OAuth、Apple 购买及业务后端部署分别验收，不由基础包发布测试代替。
