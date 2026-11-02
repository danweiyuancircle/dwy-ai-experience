# CLI 共享 Skills 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用户级单份 Skills 副本，项目和全局使用目录链接，升级后刷新一次即可更新所有已迁移项目。

**Architecture:** 新增共享副本模块，供各平台的 Skills 写入统一使用；总同步入口按平台执行全局优先去重并记录实际入口。升级命令调用新安装 CLI 的公开刷新命令。

**Tech Stack:** Node.js ESM、现有 fs-extra、node:test，不新增依赖。

**Spec:** `docs/superpowers/specs/2026-11-02-cli-shared-skills-design.md`

## Global Constraints

- 在主工作目录 develop 修改；保留已有 CHANGELOG 规则改动，不自动提交、打标签或发布。
- 共享目录为用户根下 `.dwy/skills/<name>`；链接整个 Skill 目录，父目录保持真实目录。
- 同平台全局入口优先；原真实目录先备份；用户自定义 Skills、Rules、Hooks 不扩大清理范围。
- 已通过设计确认，主代理在当前会话直接执行，完成后独立审查。

## 执行记录

- Task 1 complete：共享副本、整批失败恢复、目录链接、备份、坏链和并发互斥已实现。
- Task 2 complete：完整同步、仅 Skills、额外全局入口、实际状态和全局优先已实现。
- Task 3 complete：公开 migrate / refresh、升级后新进程刷新和使用说明已实现。
- Ruling：用户补充一键迁移要求，增加 `dwy migrate`；只迁移项目已有托管条目，不补装缺失项。
- 独立审查的三项问题均有失败重现测试，修复后 CLI 全量 108/108 通过；额外覆盖六种取消选择时的根链接保护。
- 未提交、打标签、发布，未修改真实用户全局 Skill 配置；Windows junction 未在真实 Windows 系统验收。

## Review Focus

- 刷新失败、链接创建失败：旧副本和原入口不能丢失。
- 软链接及坏链：重复执行、扫描和清理不能遗漏，也不能删除链接目标。
- 项目和全局同时选择：先全局成功，再去重项目；状态和默认选择与实际入口一致。
- 新包删除某 Skill：保留仍被链接的共享旧副本并报告，不自动清空其他项目使用的内容。
- pnpm 升级路径变化和取消同步：新进程刷新；取消不得产生共享副本或迁移。

### Task 1: 共享副本与链接

**Files:** 新建 `dwy-cli/src/skill-store.js`、`dwy-cli/tests/skill-store.test.js`。

**Interfaces:**
- `prepareSharedSkills({ skills, homeDir })` 返回 sourcePath 指向共享副本的 Skills。
- `linkSkill({ skill, dest, backupRoot })` 创建目录链接，旧真实目录备份，失败恢复。
- `refreshSharedSkills({ sourceDir, homeDir })` 只刷新已经安装的共享 Skills，返回更新及保留项。

- [x] 先写测试，验证两个入口共享内容、完整目录刷新、旧文件移除、真实目录备份、坏链修复、失败恢复、删除入口不删目标。
- [x] 运行 `node --test dwy-cli/tests/skill-store.test.js`，确认缺少实现时失败。
- [x] 用现有 fs-extra 与 Node 文件系统实现副本准备和链接，不新增配置或依赖。
- [x] 运行同一测试，全部通过。

### Task 2: 同步和全局优先

**Files:** 修改 `dwy-cli/src/sync.js`、`dwy-cli/src/sync-codex.js`、`dwy-cli/src/sync-opencode.js`、`dwy-cli/src/sync-global-skills.js`、`dwy-cli/src/sync-all.js` 及对应测试。

**Interfaces:** 消费 Task 1 的共享副本和链接函数；各平台沿用已有入口并支持注入临时用户根。

- [x] 先补失败测试：项目迁移、全局去重、OpenCode 兼容发现目录、仅 Skills 模式、状态和默认勾选、未选择但已管理的重复项、取消无写入。
- [x] 各平台 Skills 写入链接，Codex 扫描跟随目录链接并识别坏链。
- [x] 总入口准备副本、先写额外全局入口，再按实际全局存在过滤项目写入与状态；去重前备份真实目录。
- [x] 运行同步相关测试，确认个人 Skills 和其他配置的保留行为不变。

### Task 3: 刷新、升级与交付

**Files:** 修改 `dwy-cli/bin/index.js`、`dwy-cli/src/self-upgrade.js`、`dwy-cli/src/cli-help.js`、对应测试和现有使用说明。

- [x] 先补失败测试：公开 `dwy refresh`、升级成功调用新 CLI 刷新、已是最新也刷新、刷新失败不报告成功。
- [x] 按用户补充要求实现公开 `dwy migrate`：自动发现老项目已有托管 Skills，备份并迁移，保留个人项和其他配置，重复执行幂等。
- [x] 刷新入口消费 Task 1；升级后使用新进程，避免复用旧模块路径。
- [x] 补充使用方式和首次迁移限制。
- [x] 运行 `pnpm --filter create-dwy test` 和 `git diff --check`，完成独立审查并修复实际问题。
