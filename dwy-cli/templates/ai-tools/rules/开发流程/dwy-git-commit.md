---
description: Git 提交硬约束（先同步远程、敏感信息、message 格式、AI 署名）。命令和冲突步骤见 skill dwy-git-commit。无 paths，每次注入；不提交时忽略。
---

# Git 提交（硬约束）

只在本次任务包含提交、commit message、`git pull` / rebase 冲突、提交前检查时遵守。只改代码、不提交时忽略本文件。命令、冲突步骤、敏感名单见 skill `dwy-git-commit`。和本文件冲突时以该 skill 为准。

1. 先 `git fetch origin`，再 `git pull --rebase --autostash`。冲突未清零禁止新 commit。没有 remote，或远程没有同名分支，可以跳过并写明原因。
2. message 用 `git commit -F` 或单引号。禁止双引号里带反引号或 `$(...)`。
3. 提交前看暂存区。密钥、证书、真实数据、明文连接串不进仓库。
4. 格式 `<type>(<scope>): <subject>`。`type` 只用 `feat` / `fix` / `refactor` / `chore` / `docs` / `test` / `perf` / `style` / `ci`。subject 用中文动宾，不超过 72 字。
5. 删掉 AI 署名和「由 AI 生成」声明，含环境自动塞入的 `Co-authored-by`。hook 拦住就删掉再交，不绕过。
