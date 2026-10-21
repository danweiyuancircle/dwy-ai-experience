# 私有共享仓库迁移验收

## 交付入口

- 统一源码：私有仓库 `danweiyuancircle/dwy-ai-experience`，本机入口 `~/WebstormProjects/dwy-shared`。
- 固定版本：[0.4.1 私有 Release](https://github.com/danweiyuancircle/dwy-ai-experience/releases/tag/0.4.1)，源码提交 `bb5bc480d0c3bace0252c443b48a2b53765edabc`。
- [正式发布 Actions](https://github.com/danweiyuancircle/dwy-ai-experience/actions/runs/39536538222) 全部成功，实际上传 5 个 npm tgz、2 个 Python wheel、2 个 sdist，以及 `release-manifest.json` / `SHA256SUMS`；工作流重新认证下载并核验发布字节。
- 早先的 `0.4.0` 标签保留，但因 uv 生成的目录忽略标记被严格白名单拒绝，没有完整 Release；消费入口统一使用 `0.4.1`。

## 模块边界

- `apple/`：原 AppleAppKit 通用模块、模板、脚本与文档；根 `Package.swift` 暴露原产品名。
- `modules/auth/apple/`：AuthCore、Google iOS 适配。Google-only；未新增业务 App 登录页面。
- `backend/`：EAPI `0.11.1`，提供统一 Principal / IdentityVerifier 合同。
- `modules/auth/backend/`：`dwy-app-auth 0.1.0`，Google 用户登录、刷新、设备会话、删号，与独立管理员 Cookie 认证；不依赖 App Cloud 或具体业务应用。
- `modules/auth/web/`：`@dwydev/auth-web 0.1.0`，管理员登录组件、同源 API、内存会话；宿主注入品牌和路由。
- App Cloud 保留三应用独立数据/迁移与业务装配，原 `cloud-auth` / `cloud-kernel` 兼容入口重导出共享实现。

## 正式发布验证

同一个 `0.4.1` 标签流水线执行：Python 307 passed / 2 skipped；EUI 793、EKIT 232、admin-kit 8、auth-web 25 全部通过；CLI 56 tests / 0 failures；Swift 43 tests / 0 failures；真实 iOS simulator SDK 的 AuthGoogleIOS 编译通过。私有发布策略 8 tests、Apple 模板生成 3 tests 在发布前通过。

本机认证下载同一 Release 后，全量大小/SHA256 校验通过。App Cloud 的 Python 依赖已固定为实际发布 wheel，Web 四个共享依赖固定为同一发布 tgz，uv/pnpm 锁文件均已重建，不含临时 worktree 依赖。后端 lint 通过、327 tests passed / 5 skipped；管理后台 83 tests passed，类型检查与生产构建通过。五个 tgz 在全新目录以严格 peer 规则安装通过，认证 API / 内存会话 / Vue SSR smoke 与 CLI `--help` 通过。

两个正式发布 wheel 在独立 Python 3.11 环境安装通过；认证包 smoke 确认 App Cloud / cloud-kernel / 三业务包均未安装，EAPI 身份合同、Google 会话协议、管理员 Cookie 隔离和删号成功。更新前端静态资源后，App Cloud 八个 workspace 包的 wheel/sdist 构建成功；ADBox、四象限、RightFlow 三个全新单应用环境显式重装本轮 wheel，各自完成迁移、固定表、配置继承/审计、生命周期和默认拒绝 smoke，另外两业务包缺席。

私有发布使用作业临时 `GITHUB_TOKEN`，不使用 npm/PyPI 长期发布凭据。旧公开工作流已禁用，npm 的 `private: true` 与 Python 的 `Private :: Do Not Upload` 阻止误公开。下载器验证仓库可见性、固定标签、文件集合、大小与 SHA256，并记录源提交；本轮另外通过远端 Git 与消费者解析核对标签提交。

## 消费者与后续运行边界

原生项目结果见 [消费者迁移记录](consumers.md)。ADBox 的 [独立只读访问 CI](https://github.com/danweiyuancircle/tv_plus/actions/runs/39536771900) 已成功读取固定标签；只读 deploy key 仅授权共享仓库读取，未触发 TestFlight 或 App Store 上传。

三个消费者从真实私有 Git 解析到同一 `0.4.1` 提交，最终受锁保护的 Swift 测试分别为 RightFlow 186（4 skipped）、四象限 149、ADBox 1713，均零失败；ContextKit/macOS、Quadrant/iOS Simulator、QuadrantMac、ADBox/iOS Simulator、ADBoxMac 五个应用壳均实际构建成功。三份根锁与 Xcode 共享锁逐字一致，GoogleUtilities 固定为 `8.1.4`，重新运行 XcodeGen 会自动复制 canonical 锁。RightFlow 的三项依赖配置以 `8ac35cf` 推送 main，ADBox 对应配置以 `78e481c` 推送 preview；四象限当前无 Git 仓库，配置保存在原工作区。并行业务编辑的时间边界见消费者报告。

旧 `apple-app-kit` 已设为私有，认证访问有效、匿名 GitHub API 返回 404。原 `ios-arc` 的未提交认证源码保留，只加迁移入口说明。

真实 Google OAuth 仍需要开发者自己的 Google Cloud OAuth 客户端配置、iOS URL scheme 与后端 audience。测试中的验证器替身用于校验协议，不表示真实账户已完成授权。生产数据库、Apple 购买和设备交互验收不在源码迁移测试中。App Cloud 的 PostgreSQL 场景需要测试 DSN；当前本机没有 Docker daemon，未声称 Docker 镜像构建或生产部署成功。

并行整理工作已将 App Cloud 根目录建立为独立私有仓库 `danweiyuancircle/app-cloud`，管理前端仍是独立私有仓库 `danweiyuancircle/app-cloud-admin`。本轮前端认证提交 `25af11e` 已推送；其后的目录说明提交由并行工作完成。按用户最新要求，App Cloud 的 GitHub workflow 已移除，远端旧工作流已停用；提交 `9611864` 已推送。验收入口改为本地 `backend/scripts/check-local.sh`，完整实际执行 exit 0，保留上述后端 327 / 前端 83 及三个独立 wheel 环境验证，不再要求配置跨仓库 CI token。

共享主工作区存在并行的设备指纹开发改动，原样保留；本报告的发布、安装和原生构建结论针对固定 `0.4.1` 标签，不覆盖后续并行功能。
