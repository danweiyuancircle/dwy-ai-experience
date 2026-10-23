# 首批实施记录

状态：下文保留候选制品阶段的验证记录；最终发行结果见本文末尾。后续用户已授权提交、推送、发行和主干集成。

Plan: docs/superpowers/plans/2026-10-23-shared-admin-phase1.md

## 已验证

- Task 1：组件先 RED（20 份新文件缺入口，旧 8 项绿），迁移后 GREEN；OverviewCard 漏导出另有 2 项 RED→GREEN。
- Task 2：原 quant 分页 13 项移植后绿；合并行为测试 12 项 RED，补齐 error/invalidate/reset/dispose 后共享包 87 项全部通过。
- Task 3：实际 tarball 的子入口/类型检查先因缺入口 RED；补多入口后通过。发现 SFC 虚拟模块查询串导致实际加载失败，改为 bundler entryFileNames 模板后解决；Slots 显式类型解决声明循环推断，并使声明诊断成为 build 失败条件。
- Task 3：独立安装本轮 admin-kit/EUI/ekit 实际 tgz，TypeScript 和 Vite 打包后的真实 EUI SSR 通过。
- Task 3：认证 Provider 合同已写，未增加认证运行时代码或改变两套会话。
- Task 4：quant 接入候选，前端 470 项测试、构建和 peer/CSS 验证通过。
- Task 4：App Cloud 接入候选，89 项测试、类型检查、构建与冻结严格 peer 安装通过。

## 执行裁定

- 本轮不提交/推送/发行/部署；原仓库的其他任务不受影响，工作保留在独立分支供审阅。
- 原生 task worktree 工具不能选择跨仓目标，三仓使用 Git worktree 隔离。
- 实际 SSR 验收采用产品的 Vue/Vite 模式；现有 ekit 的 dayjs 子路径不满足原生 Node 直接加载，未扩大范围修改 ekit。
- 制品验收开始使用离线缓存，发现新 pnpm 缓存布局及 Vite 可选传递依赖缺失；固定 pnpm 10.19.0，基础库用本轮 tgz，其他固定依赖从官方 npm registry 安装。
- App Cloud 相对 file 依赖触发 pnpm 自动 peer 解析问题；关闭 workspace 自动安装 peer，保留严格检查，并按原锁定版本显式提供已有运行 peer，避免重复 Vue/EUI。

## 最终验收

- 最终候选 SHA256：904ef184ae3d60b512cf1cfbbc6ede022e3768628c4375db187da92c42d79637。
- 共享包完整测试：26 文件、87 项通过；最终 build 无 TypeScript 声明诊断。
- 独立 tarball 的类型、子入口和真实 Vue/Vite SSR 验收通过。
- quant：470 项通过；App Cloud：89 项通过；两者类型检查与构建通过。
- 最终候选与完整测试时的候选逐文件比较，全部 JS/CSS/d.ts 一致；仅 README 与开发依赖键顺序变化。两产品刷新最终制品摘要后，冻结安装和构建再次通过。
- 独立复核未发现 Critical/Important 源码问题；构建配方漏写基础包构建步骤已补齐。
- 两消费方均验证了安装路径、单一 Vue/EUI 及最终 scoped CSS。没有源码 alias 冒充制品消费。
- 原 checkout 未由本轮修改；本批保留三仓独立工作树，未提交、合并、推送、发行或部署。

全部首批任务完成。完整认证 UI 和访问控制新能力仍按设计留待后续批次。

## 后续审计与发行

- EUI 追加普通输入原生属性保留、多种控件的真实标签/错误描述关联，以及清除校验时保留草稿的修复；最终 89 个测试文件、815 项测试通过。
- admin-kit 最终 28 个测试文件、98 项测试通过；EUI peer 下限为 ^2.7.2。
- EUI 2.7.2 先经 GitHub Actions OIDC 发布，确认公共安装成功后，再发布 admin-kit 0.3.0。两者 tgz 完整性与源码提交均已核对。
- 从公共 npm 精确安装两个正式版，在全新消费者中通过严格 peer、TypeScript、子入口及真实 Vue/Vite SSR 验收。
- 源码提交 `fefb950845ceade77135d3aaaa05f31b01fa42e2` 与 `42a585bb1eb78b297021dbd77f1838dc3ac0a129` 已合入并推送 master。
- Apple 继续使用纯版本标签，未修改 0.5.0。完整认证 UI 仍未纳入本批运行时交付。
