# Shared Admin Phase 1 Implementation Plan

状态：本文件保留最初的实施计划。后续用户授权了发行和主干集成；最终 EUI 基线提升为 2.7.2，EUI 2.7.2 与 admin-kit 0.3.0 已发布并合入 master。下文“不提交、推送或发布”为初始阶段边界，不再作为当前限制。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 将已复用的管理组合组件收进 admin-kit，以真实制品完成 quant 和 App Cloud 兼容接入。

**Architecture:** 既有根导出保持兼容，增加组件与 composables 子入口；产品 workspace 包变为兼容出口。usePagedList 合并两消费方的修复。认证仅形成下一批合同设计。

**Tech Stack:** Vue 3.5、EUI 2.7.1、TypeScript、Vite、Vitest、pnpm。

**Spec:** docs/superpowers/specs/2026-10-23-shared-admin-phase1-design.md

## Global Constraints

- 不新增运行时依赖；不改后端、既有认证、业务模型或部署。
- EUI peer 基线 2.7.1；沿用其他现有 peer。
- 组件不能依赖 @dwy/core、产品 API、Pinia 或产品 DTO。
- 保留 @dwy/components 的 root、status/tone、paged-list 出口；quant 密码字段暂留。
- Git worktree 隔离三仓，保护既有工作；本轮不提交、推送或发布。
- 本地包制品必须可复现；消费配置不能写死开发者临时绝对路径。

## Review Focus

- reset/退出/卸载后旧请求成功、失败及 finally 不能覆盖新数据或 loading。
- 错误不能伪装成正常空列表；重试必须清除旧错误。
- fetcher 附属汇总必须与列表共享 isCurrent 提交边界。
- 根/子路径导出、类型声明、peer 去重和 Tailwind 样式不能只在源码 alias 下成立。
- quant 密码字段导出和两产品现有认证/业务行为保持兼容。

### Task 1: 公共管理组合组件

**Files:** frontend/admin-shell/src/components/**、tests/components/**、src/components/index.ts。

**Interfaces:** 输出方案列明的纯展示组件、字段类型、confirmThen 和 pageSizes；不包括密码字段和分页状态机实现。

- [x] 先迁移现有组件测试，在共享包尚无对应实现时运行，确认缺少组件导致失败。
- [x] 迁移无业务依赖组件，合并 RequestFeedback/ChartCard/筛选与日期展示；保留真实 EUI 集成测试。
- [x] 加入 Vue Vitest 插件与必要的现有依赖内联配置，完整 admin-kit 测试通过。

### Task 2: 合并分页请求状态机

**Files:** frontend/admin-shell/src/composables/usePagedList.ts、src/composables/index.ts、tests/composables/usePagedList.test.ts。

**Interfaces:** usePagedList<T>(PagedListOptions<T>)，导出既有分页类型和 pageSizes；fetcher(params, { isCurrent })，返回 error、reset、invalidate 与全部旧方法。

- [x] 合并原有分页测试，新增 reset 清错误/筛选、失效保留数据、卸载防回写、附属汇总守卫与旧 finally 不清新 loading 测试；观察 RED。
- [x] 单调请求代次实现；单参数 fetcher 兼容，当前失败保留原错误对象，旧响应不修改任何状态。
- [x] 跑完整 admin-kit 测试，验证两消费方既有分页合同。

### Task 3: 独立制品与认证合同

**Files:** frontend/admin-shell/package.json、vite.config.ts、README.md、CHANGELOG.md、scripts/smoke-pack.mjs、tests/fixtures/**；frontend/auth-web/docs/provider-contract.md。

**Interfaces:** 新子路径 components、composables、status/tone、paged-list；真实 ESM 与 d.ts 制品。

- [x] 编写实际制品消费者验证，缺少子入口/导出时失败；包含真实组件渲染和类型检查。
- [x] 配置多入口、保留根 API、EUI peer 下限，构建候选版本并 pack。
- [x] 从 tarball 干净安装，验证 exports、types、无产品依赖、实际 Vue/EUI 共享实例。
- [x] 写认证 Provider 合同：必需生命周期、可选能力组、密码与重置差异、错误/导航/挑战端口、Cookie/JWT 模式和范围外能力；不写运行时代码。

### Task 4: 两产品兼容接入

**Files:** 各产品 packages/components/src/index.ts、status/tone.ts、paged-list/index.ts、package.json、lockfile、主题扫描入口、README 与测试清单。

**Interfaces:** @dwy/components 保留旧导出；实际实现来自共享包制品；quant 密码字段继续本地导出。

- [x] 接入前先运行原组件回归，记录基线；增加合并分页行为的消费者验证。
- [x] 使用真实共享 tarball 替换重复实现，配置相对本地制品消费与可复现准备命令，保留必要兼容路径。
- [x] 两产品分别执行完整前端测试和构建，不改其他业务逻辑。
- [x] 比较 diff、检查敏感内容与无关变化；独立复核最终改动。

## Execution Rulings

- 用户已批准完整方案及其首批范围，依项目并行规则执行，不另设重复审批步骤。
- 当前任务的原生 worktree 工具不能选择跨仓目标，三仓均使用 Git worktree 建立独立分支。
- 不执行技能模板中的自动提交/推送；保留可审阅工作区与验证记录。
