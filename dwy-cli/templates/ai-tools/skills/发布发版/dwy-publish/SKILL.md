---
name: dwy-publish
description: "Use when 用户要求整理工程版本、更新 changelog、打版本 tag、发版、发布或部署上线。"
---

# 工程版本管理与发布编排

先识别工程及变更，再为需要更新的工程维护版本、changelog 和 tag；是否发布及发布方式按用户意图和项目上下文判断。

## 流程

1. 读取仓库指令、结构、构建配置、版本来源、changelog、Git 状态和历史 tag，识别独立工程及共享版本边界。依据实际依赖判断共享代码影响；不要把每个子目录当成独立工程。优先遵循用户指定范围，分不清边界时询问。
2. 逐工程列出变更、版本来源、changelog 路径、tag 命名、版本类型、是否需要发布和 tag 触发器。检查上次对应 tag 后的提交及本次相关的未提交变更；不要把不属于本次的改动纳入提交。
3. 对本次需要更新的工程，按 `../dwy-semver` 确定版本级别、beta/rc 或正式版，按 `references/version-sync.md` 同步版本；按 `references/changelog.md` 更新该工程 changelog，再按 `references/git-tag.md` 提交和打 tag。无变更工程不创建空版本。已覆盖本次代码的现有版本可复用，不重复升版或打 tag。
4. 确定是否发布：仅版本管理时结束；需要发布或部署时，读取项目约定及现有 CI、构建和部署配置，判断渠道和命令。遵守仓库的发布和授权规则，不套用固定发布方式；证据不足时询问。不根据分支判断版本类型或发布流程。
5. **部署上线闸门**：有新代码要上线，AI 自动检查并补齐对应工程的版本更新、changelog 和 tag，不逐项要求用户确认。自动校验 tag 指向包含全部拟部署代码、版本和 changelog 的提交，构建或部署使用该提交或其已验证产物。补齐并校验通过后继续部署；无法补齐或校验失败时停止部署并说明原因，不能以赶时间或已有构建替代。先完成项目要求的测试和适用的安全检查；SDK 对外发布前读取 `../dwy-sdk-spec`。
6. 推送 tag 前检查远端工作流及其他自动触发器：若推送会发布，先完成所有发布闸门并确认本次已获发布授权。仅要求版本管理而推送会触发未经授权的发布时，保留本地 tag 并报告，不能推送或擅自更改 workflow。
7. 已获授权且满足闸门时，按项目实际配置执行发布；需要 GitHub Actions 打包时读取 `../dwy-github-action-publish` 和相应平台参考文件。按 `references/monitor-notify.md` 监控并验证实际结果。

仅重发、重跑或回滚**完全相同的已记录版本和产物**，可复用对应 changelog、版本及 tag；必须核实代码和产物身份。有新代码则不是重发，必须完成新版本的全部闸门。仅环境配置变更按项目约定记录和验证，不得借此夹带新代码。

## 参考文件

- 版本和记录：`references/version-sync.md`、`references/changelog.md`、`references/git-tag.md`。
- 发布配置：仅需要发布时读取 `references/publish-config.md`，必要时使用 `bash scripts/release_config.sh`。
- 平台：`references/frontend-deploy.md`、`references/backend-deploy.md`、`references/ios.md`、`references/android.md`、`references/harmony.md`、`references/generic-release.md`。

版本、tag 或发布目标存在歧义时先核实；不可识别时询问。删除或覆盖远端 tag / release 前必须获得用户明确授权。输出各工程的版本、changelog、tag、是否推送和实际发布验证结果。
