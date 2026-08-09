# iOS App Store Release Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建由 dwy 同步的 iOS/macOS App Store 上架 Skill，并将 API 凭据只保存到用户私有目录。

**Architecture:** Skill 以 Markdown 编排上架工作流，用一个无外部依赖的 shell 脚本维护 `/Users/chances/.dwy/app-store-connect/` 的非秘密配置。发布包模板与参考文档保持 API 自动化、网页补齐、截图分平台和 ICP 非阻塞策略一致。

**Tech Stack:** Markdown、POSIX shell、`jq`、App Store Connect API、Playwright。

## Global Constraints

- 模板必须位于 `dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/`。
- API 私钥、审核密码和 Cookie 不得写入 Skill、仓库或发布包。
- 产品页仅 `zh-Hans` 和 `en-US`，默认全地区可售；ICP 缺失不阻塞其它地区。
- 提交审核、发布和价格上调必须二次确认。

---

### Task 1: 用户私有配置脚本

**Files:**
- Create: `dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/scripts/appstore_config.sh`
- Test: `dwy-cli/tests/ios-app-store-release.test.js`

**Interfaces:**
- Consumes: `init|get|set|reset` 子命令和显式配置根目录。
- Produces: 权限为 `0700` 的目录与权限为 `0600` 的 `config.json`。

- [ ] **Step 1: 写失败测试**：断言 `init` 创建私有配置，`set` 持久化 Issuer ID/Key ID/团队，`reset` 删除配置。
- [ ] **Step 2: 运行测试并确认缺少脚本导致失败**
- [ ] **Step 3: 实现最小 shell 脚本**：用 `jq` 生成 JSON，拒绝空 Issuer ID/Key ID，禁止私钥内容作为参数。
- [ ] **Step 4: 运行测试与 `bash -n`**

### Task 2: Skill 模板与参考资料

**Files:**
- Create: `dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/SKILL.md`
- Create: `dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/assets/appstore-submission.yaml`
- Create: `dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/references/api-workflow.md`
- Create: `dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/references/screenshot-workflow.md`

**Interfaces:**
- Consumes: 用户项目、私有配置与发布包。
- Produces: 已确认发布包、API/网页填充动作、截图上传清单与 ICP 待办。

- [ ] **Step 1: 写失败测试**：断言模板包含双语、全地区、ICP 非阻塞、二次确认与私有目录约束。
- [ ] **Step 2: 运行测试并确认模板不存在导致失败**
- [ ] **Step 3: 写最小模板与参考资料**：明确 API 优先、Playwright 补齐、真实应用截图和不可自动决定的法律项。
- [ ] **Step 4: 运行测试与 Skill 结构校验**

### Task 3: 回归验证

**Files:**
- Modify: `dwy-cli/tests/ios-app-store-release.test.js`

- [ ] **Step 1: 运行单测**：`cd dwy-cli && node --test tests/ios-app-store-release.test.js`。
- [ ] **Step 2: 运行完整 CLI 测试**：`cd dwy-cli && pnpm test`。
- [ ] **Step 3: 运行 `quick_validate.py` 与敏感字段扫描**。
