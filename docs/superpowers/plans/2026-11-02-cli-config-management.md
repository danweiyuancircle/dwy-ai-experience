# CLI 配置启停实施计划

> **For agentic workers:** 使用 superpowers:executing-plans 按任务顺序直接实施；提交仅在用户后续要求时执行。

**Goal:** 全局与项目可显式管理通用规范和 Hooks，按有效全局配置继承并安全去重。

**Architecture:** 复用 syncAll 的只读计划与平台适配器；继承识别集中到 sync-inheritance.js。基线和 Rules 独立写入，动作记录到现有平台状态。

**Tech Stack:** Node.js ESM、fs-extra、@clack/prompts、node:test；不新增依赖。

**Spec:** `docs/superpowers/specs/2026-11-02-cli-config-management-design.md`

## Global Constraints

- 未选择类型保持原样，移除须显式，确认前只读；原有未提交内容保留。
- 项目基线在任一所选 CLI 有全局提供者时禁止安装；Hooks 按名称与平台分别继承。
- 保留原生平台路径、自定义 CODEX_HOME、已有 Skills 刷新及备份语义。
- 直接在 develop 实施；提交、发布及真实用户配置更新按后续用户授权执行。

## Review Focus

- 通用规范与 Rules 共用文件时不能互删。
- 全局缺脚本或注册信息时不能跳过项目安装。
- 用户移除后不能被默认值重新启用。
- 全局配置及项目配置别名重合时不能删除唯一提供者。
- 配置路径、脚本路径和个人 Hooks 混用时只清理确认的托管项。

### Task 1: 基线独立启停

Files: `dwy-cli/src/sync-codex.js`、`dwy-cli/src/sync-inheritance.js`、`dwy-cli/tests/config-management.test.js`。

Interfaces: `syncBaselineDoc(baseline, dest)` 只更新基线块，空文本移除；`hasManagedBaseline(dest)`、`globalBaselinePath(platform, homeDir, codexHome)` 只读识别。

- [x] 先添加基线与 Rules 独立、手写内容保留、混合平台继承的失败用例。
- [x] 观察失败，实施最小写入与识别能力，再运行该测试文件。

### Task 2: Hooks 有效继承和移除

Files: `dwy-cli/src/sync-inheritance.js`、`dwy-cli/src/sync.js`、`dwy-cli/src/sync-codex.js`、`dwy-cli/src/sync-plan.js`、`dwy-cli/tests/config-management.test.js`。

Interfaces: `globalHookNames({platform, sourceDir, homeDir, codexHome})` 返回有效名称 Set；`buildSyncPlan` 接收 `contentActions`，其中 hooks/baseline 使用 sync 或 remove。

- [x] 添加全局有效注册、缺脚本、缺注册、部分覆盖、显式移除及个人配置保留的失败用例。
- [x] 复用生成命令和配置合并逻辑，清理注册项与脚本保持一致，所有持久写入列入计划。
- [x] 添加路径链接保护和全局当前项目去重用例并验证。

### Task 3: 交互与状态

Files: `dwy-cli/src/sync-all.js`、`dwy-cli/src/sync-plan.js`、`dwy-cli/tests/sync-selection.test.js`、`dwy-cli/tests/config-management.test.js`。

Interfaces: `syncAll` 接收可选 `contentActions`；旧脚本不传动作时沿用 sync。平台状态 baseline 布尔值用于默认选择；原其他字段保留。

- [x] 添加全局首次默认、移除后不复选、项目基线选项、全局继承下禁止启用和取消无写入的真实终端失败用例。
- [x] 加入整组 Hooks 和通用规范动作步骤，显示继承状态和路径；保存实际处理类型状态。
- [x] 重跑范围、分类、部分覆盖、迁移等旧用例，更新与新约定冲突的断言。

### Task 4: 文档、版本和审查

Files: `README.md`、`dwy-cli/src/cli-help.js`、`dwy-cli/CHANGELOG.md`、`dwy-cli/package.json`，审查记录位于 `.dwy/reviews/cli-config-management/review.md`。

- [x] 更新帮助、文档及带版本日期的变更记录，开发版本设为 0.24.0。
- [x] 运行 `pnpm --filter create-dwy test`、`git diff --check`，完成独立只读审查及必要修复复测。
- [x] 记录快照、验证、未覆盖环境；提交发布按后续用户授权执行。

完成记录：CLI 146/146 全量通过，独立只读复审无剩余阻断。发现并修复旧原文基线与 Rules 同轮处理顺序问题；完整记录见 `.dwy/reviews/cli-config-management/review.md`。

实施验收后，用户已授权提交代码、发布 0.24.0 并更新本机全局 CLI。
