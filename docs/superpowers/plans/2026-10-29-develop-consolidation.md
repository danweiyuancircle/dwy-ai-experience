# develop 功能整合与验证计划

> **For agentic workers:** 使用 superpowers:executing-plans 按任务执行；已完成的历史功能通过补丁比对确认，不以旧分支提交数判断缺失。

**Goal:** 将其他分支已提交的有效功能统一收敛到 develop，尤其保证 Webhook 功能复用同一实现并通过跨包回归。

**Architecture:** 以当前 develop 为集成基线，按提交补丁和当前文件内容比较旧分支。保留已合入的较新实现，只补真正遗漏的功能及整合问题；旧工作目录里的未提交扩展单独列明范围。

**Tech Stack:** Git、Python/pytest、Vue/Vitest；不新增运行时依赖。

**Spec:** 本轮用户要求：合入其他分支的有效功能，重点收口 Webhook 重复功能。

## 全局约束

- 在主工作目录 develop 上操作，保留现有分支、worktree 和标签。
- 不将历史脱敏前的提交重新接入公开主干；以功能和补丁等价性确认是否已收口。
- 第一阶段默认只整合各分支已提交功能；用户随后明确授权“一起整合然后提交”，第二阶段纳入原工作目录中的未提交认证扩展，仅提交不推送。
- 保留本轮开始前已有的两个苹果经营日报设计、计划文件，不纳入本轮提交。

## 审查重点

- 分支提交 ID 不同但补丁一致时，不能重复移植相同实现。
- 已合入的后续安全与生命周期修复不能被旧工作目录内容覆盖。
- Webhook 发送、评论、购买详情、日报和周报继续通过现有包导出与调用。
- 独立包测试通过后，还必须按跨包 CI 命令检查测试模块命名冲突。
- editable 环境的安装版本必须与当前包清单一致，避免把陈旧元数据误判为源码问题。

## 任务 1：核对分支和工作目录

- [x] 刷新远端引用，确认 develop 与 origin/develop 一致。
- [x] 检查本地与远端功能分支，使用 git cherry 区分等价补丁和未包含的补丁。
- [x] 核对历史重写后的对应提交；剩余差异为旧文档脱敏与已失效路径，无未合入的已提交业务功能。
- [x] 专项核对 Webhook：旧认证设置分支的 6 个相关历史提交均有等价补丁，其余分支无独有 Webhook 补丁。
- [x] 管理员旧工作目录：97 个文件与 develop 相同；其余源码、测试仅末尾空白不同，文档为 develop 补充的最终发行说明。
- [x] 单列认证旧工作目录的 33 个未提交差异，包含准入、邮箱变更和账号管理扩展；未纳入默认整合范围。

## 任务 2：修复跨包测试收集冲突

**Files:**
- Rename: `backend/packages/webhooks/tests/analytics/test_runtime.py` → `backend/packages/webhooks/tests/analytics/test_analytics_runtime.py`
- Modify: `backend/packages/webhooks/tests/TEST_CASES.md`

- [x] 运行后端、认证、Webhook 和脚本组合测试，重现两个 test_runtime 模块的 import file mismatch。
- [x] 仅重命名日报运行时测试文件，同步测试文档，不改变测试和产品逻辑。
- [x] 重跑完整组合测试与 Webhook Ruff。

## 任务 3：最终确认

- [x] 管理员包回归：28 个文件、98 项测试通过。
- [x] 确认组合 Python 回归与 Webhook lint 通过：827 passed、3 skipped、41 subtests passed；3 项既有弃用警告。
- [x] 确认差异检查及独立审查通过；审查无 Critical、Important 或 Minor 问题，重命名文件与原文件逐字节相同。

交付约定：仅提交测试重命名、对应测试清单和本计划，提交后核对 develop 与远端同步状态。

第一阶段审查边界：当时未提交认证扩展等待范围确认，后续授权与整合见第二阶段；历史补丁等价性不替代所有功能的端到端正确性证明；未进行线上投递或发布验收。

## 第二阶段：未提交认证扩展

来源：`feat/paid-settings-auth-20261027` 的原工作目录；保留该目录的原始改动。

- [x] 先合并新增测试，验证原子注册准入等接口缺失；Swift 使用实际 Xcode 工具链复现账号管理协议缺失。
- [x] 三方合并通用准入、邮箱变更、登录入口列表、刷新回调、Swift 账号管理接口与双端认证 UI；保留 develop 较新的会话与 Apple 安全修复。
- [x] 原 `AppleConfig` / `AppleIdentityProvider` / `AppleSignInCredential` 单令牌方案由现有服务端挑战与授权码流程覆盖，不引入第二套 Apple 身份实现。
- [x] 修复 Apple 专用登录绕过准入和 Swift Apple 交换未携带准入证明的问题，均先以回归测试复现。
- [x] 独立审查发现 Apple-only 账号无法使用通用重新认证；补充绑定主体和用途的 Apple 管理挑战、一次性 proof 及 Swift 承载接口，跨主体、跨用途、重放、切号和取消均有回归覆盖。
- [x] 同步新增 schema、宿主迁移、API 约束与测试清单；修正文档中“Apple 官方控件”的表述。
- [x] 隔离已提交基线与本轮认证改动，Python 885 passed、4 skipped、41 subtests passed；跳过项包含需要专用 PostgreSQL 环境的锁交错测试。
- [x] Swift 全量测试通过；认证核心 71 项、认证 UI 12 项通过。
- [x] iOS 模拟器 SDK 的 AuthUI 目标构建通过。验证期间临时移开本机失效的 GRDB 文件镜像配置，完成后恢复；未改动锁文件或依赖版本。
- [x] 并行 Webhook 工作落盘并刷新 editable 版本元数据后，当前工作区组合回归最终为 894 passed、4 skipped、41 subtests passed；认证相关 Ruff 和差异检查通过。

同目录同时存在另一组 Webhook 工作；本轮提交不包含那些改动。组合回归一度出现以下并行工作失败，隔离基线后本轮改动全绿：`test_lifespan_ownership_shutdown_order_and_public_state` 的两个参数实例、`test_download_query_is_redacted_without_disabling_caller_http_logs` 的两个参数实例、`test_runtime_stops_tasks_before_host_database_is_disposed`。

交付：只暂存认证、文档、Swift 配置及本轮沉淀的补丁上下文规则；不提交其他工作目录或并行任务的未提交改动，不发布包、不迁移生产数据库、不推送。

验证命令：

```bash
ci/.venv/bin/python -m pytest backend/tests backend/packages/auth/tests backend/packages/webhooks/tests scripts/tests -q -o asyncio_mode=auto
ci/.venv/bin/ruff check --config backend/packages/webhooks/pyproject.toml backend/packages/webhooks/src backend/packages/webhooks/tests
pnpm --dir frontend/admin-shell test
git diff --check
```
