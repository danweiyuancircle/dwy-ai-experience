# 私有共享仓库迁移实施计划

**Goal**：AppleAppKit 与现有认证能力迁入 dwy-shared，以私有源码及私有产物交付，完成真实 CI 发布和消费者安装验证。

**Architecture**：根 Package.swift 暴露稳定 Apple 产品，源码按 apple 与 modules/auth 归属。认证分客户端与 EAPI 后端，Google 用户会话与管理员 Cookie 会话独立；业务库不共享账户/数据库。Python、Swift、npm 独立构建。

**Tech Stack**：现有 SwiftPM、Vue/pnpm、FastAPI/dwyeapi/uv；不新增运行时第三方依赖。

**Spec**：用户已在当前会话批准迁移分析，并明确要求 EAPI 封装、仓库私有化、验证发包、全部完成后验收。

## Global Constraints

- Google-only；不新增邮箱验证码或 Apple 登录。
- 不丢弃 ios-arc 未提交与未跟踪的认证代码；不迁入 .git、.build、node_modules、数据库、真实 .env、证书或密钥。
- 稳定 Swift product 名称；Apple 目标最低 iOS 17、macOS 14。
- 私有源码和后续新产物不得向公共 npm/PyPI 发布。保留历史公开版本，新增发布走 GitHub Actions，使用短期工作流身份，不引入长期静态发布凭据。
- 独立分支工作；提交前同步远端、仅暂存本任务文件、检查敏感内容及 staged diff。用户已授权完成必要提交、推送和实际私有发布。
- 迁移保留行为和迁移历史；不将产品商品目录、任务规则、管理业务查询搬入公共认证库。
- 每项新增/修改行为先验证失败再实现；机械搬迁用来源清单/哈希与原有测试保障。

## Review Focus

- 干净环境真正安装私有产物，避免 uv 路径包缓存掩盖旧代码。
- 身份合同迁移后 Principal 类型与 Pydantic 校验保持一致，不引入跨应用/跨管理员认证。
- 包构建不夹带秘密、其他应用和测试缓存；发布前再次校验仓库 private。
- SwiftPM 私有远端真实解析、SPM 可识别标签及所有消费者锁文件一致。
- EAPI 0.10.1→仓库当前版本的兼容变更有回归，不把升级当机械移动。

### Task 1: Apple 框架和客户端认证迁移

**Files**：新增根 Package.swift/Package.resolved、apple/**、modules/auth/apple/**。
**Consumes**：原 ios-arc 仓库当前完整框架源码、模板、脚本、测试及文档。
**Produces**：同名 CoreKit/LogKit/L10nKit/CacheKit/DesignCore/DesignKitIOS/DesignKitMac/PurchaseCore/AuthCore/AuthGoogleIOS；Package.swift 位于仓库根。

- [ ] 记录迁移来源及 SHA256；原目录保留，迁入当前未提交 AuthCore/AuthGoogleIOS。
- [ ] 保持所有 target/product 与依赖版本，调整 target path；AuthCore/AuthGoogleIOS 物理归入 modules/auth/apple。
- [ ] 模板生成器改为当前仓库 URL，保留按版本引用；测试生成结果不含旧仓路径。
- [ ] swift test、iOS simulator AuthGoogleIOS 编译、模板 smoke；报告每项实际结果，不预报真实 OAuth。
- [ ] 输出 docs/migration-reports/apple.md 和来源清单；主执行者统一提交。

### Task 2: 基于 EAPI 的认证后端

**Files**：modules/auth/backend/**、backend/src/dwyeapi/identity.py（如需）、相关测试；app-cloud 中 cloud-auth 仅保留兼容入口。
**Consumes**：app-cloud/packages/cloud-auth，现有 dwyeapi.ApiResponse、异常、资源工厂。
**Produces**：独立 distribution dwy-app-auth、import dwy_app_auth；不依赖 app_cloud 或 cloud_kernel，包含用户与管理员两个明确入口。

- [ ] 迁移 Google 用户认证/刷新/设备/删号及测试；Principal/验证器合同落 EAPI，cloud-kernel 兼容重导出，保持同一类型。
- [ ] 封装管理员认证配置/服务/HTTP装配，配置显式注入；不搬业务查询/配置管理。
- [ ] 先回归现有协议，再验证错误 audience、跨用户、刷新重放、删号/会话及 Cookie/Same-Origin 边界。
- [ ] app-cloud 接入新私有包及 EAPI 当前版本，保留各应用迁移、数据和旧 Python 兼容入口；完整测试与三个独立安装 smoke。
- [ ] 输出 docs/migration-reports/auth-backend.md。

### Task 3: 管理员 Web 登录复用模块

**Files**：modules/auth/web/**、pnpm-workspace.yaml 和 lock；app-cloud frontend 认证接线。
**Consumes**：现有 LoginPage、管理员 Cookie API/会话逻辑；已有 eui/ekit。
**Produces**：@dwydev/auth-web，明确管理员 Cookie 认证；品牌、路由和 backend 地址可注入。

- [ ] 提取登录组件/会话/API，不搬业务导航、用户列表和交易页面，不新增未实现的 Google Web 登录。
- [ ] 组件/HTTP单测覆盖退出、错误、凭据不入localStorage、同源及输入大小；原前端构建通过。
- [ ] 输出 docs/migration-reports/auth-web.md。

### Task 4: 私有发布与仓库整合

**Files**：.github/workflows/private-release.yml、发布/安装脚本、既有公开发布工作流/包配置、README/AGENTS。
**Produces**：GitHub Actions 实际构建的 npm tgz、Python wheel/sdist 和 SwiftPM tag，私有 GitHub Release 保存产物与 SHA256 清单。

- [x] 校验 GitHub admin 权限；停用五个公开 npm/PyPI 工作流；目标仓库已改 PRIVATE。
- [ ] 既有公开工作流在源码层也禁用；私有发布运行时检查 repo private，阻止公共发布。
- [ ] 私有 Release 作为本次不依赖收费 registry/长期 token 的分发通道；npm/Python 消费者先认证下载固定发布产物再安装，Swift 用私有 Git。
- [ ] CI 运行 Python 回归、Web 构建/测试、macOS Swift 单测和 iOS simulator 编译；真实发布后下载产物验证 SHA256与安装。
- [ ] 提交/推送、合并回用户主工作区，创建 SwiftPM 0.4.0 标签及私有发布；验证远端提交/标签/可见性与匿名拒绝。
- [ ] 发布完整验收报告，列出外部 OAuth/Apple/PG 运行配置边界和可复现命令。

### Task 5: 消费者切换与旧入口收尾

**Files**：right-click/quadrant/adbox 中 AppleAppKit 配置/锁文件；ios-arc 文档；app-cloud依赖和兼容入口。

- [ ] 清点每个消费者的实际使用与工作区状态；只改已确认框架依赖路径，保留无关改动。
- [ ] 新私有 SwiftPM 标签真实解析，更新 product package identity 与 XcodeGen/Package.resolved；按项目支持执行构建/测试。
- [ ] 旧 ios-arc 保留原工作区及迁移说明，避免双源码继续演进；旧远端在消费者完成私有访问后收紧可见性，保留旧版本回退。

## 执行台账

- 2026-10-20：目标基线 3722135，master 与 origin/master 一致。使用独立 worktree，分支 codex/private-shared-20261020。
- 2026-10-20：GitHub API 证实目标仓库 admin 权限；五公开发布工作流已停用，visibility=PRIVATE。
- 2026-10-20：Ruling：本次新产物用私有 GitHub Release 分发，不沿用公开 npm/PyPI；避免新代码随包公开，也不依赖用户未开通的私有 registry。代价是消费者需要认证下载步骤，后续可平滑转私有registry。
