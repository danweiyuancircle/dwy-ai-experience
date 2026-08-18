---
description: Git Commit 规范（提交前同步远程、冲突处理、提交安全、敏感扫描、Scope、消息规范、AI 署名治理）
---

# Git Commit 规范（强制）

## 1. 适用范围

适用于所有 Git 提交流程，覆盖：

- `git fetch` / `git pull`
- `git add`
- `git commit`（含 `--amend`）
- 为提交生成或校验 commit message 的场景

项目按多人协作处理：本地未基于最新远程提交前，禁止产生新 commit。

任一步骤不通过：中止当前提交流交付流程。

## 2. 执行顺序（硬约束）

1. 拉取远程并处理完全部冲突
2. 安全写法检查
3. Stage 级敏感扫描
4. 变更范围确认
5. Scope 与 message 格式校验
6. AI 署名与生成声明校验

## 3. 提交前同步远程（强制）

多人同时改同一仓库。未拉远程就提交，会把过期基线写进历史，后续推送非快进或把冲突甩给别人。

**未完成同步、冲突未清零：禁止 `git commit`。**

### 3.1 命令

先 fetch，再 rebase 到上游。工作区有未提交改动时必须带 `--autostash`，禁止为了拉代码丢弃本地改动。

```bash
git fetch origin
git pull --rebase --autostash
```

当前分支已设置上游时，上面两条即可。未设置上游但远程存在同名分支：

```bash
git fetch origin
git pull --rebase --autostash origin "$(git branch --show-current)"
```

无 `origin` 时，对实际存在的 remote 执行同等操作。

### 3.2 冲突处理

同步产生冲突后，必须先处理完，才能做新提交：

1. 打开全部冲突文件，逐处消解 `<<<<<<<` / `=======` / `>>>>>>>`。
2. `git add` 已解决文件。
3. rebase 进行中：`git rebase --continue`（不要另开 `git commit` 顶掉 rebase）。
4. stash 弹出后再次冲突：同样消解并 `git add`。
5. 全库确认无冲突标记、无 `REBASE_HEAD` / 未结束 merge，再进入后续检查与 `git commit`。

禁止用 `git rebase --abort` / `git merge --abort` 躲冲突后直接提交。

### 3.3 可跳过的唯一情况

仅以下任一成立才可跳过同步：

- 仓库没有任何 remote
- `git fetch` 后当前分支在所有 remote 上都不存在对应分支（全新本地分支，远程无同名分支）

跳过时在回复里写明原因。其余情况一律同步。

### 3.4 失败即停

| 情况 | 处理 |
| --- | --- |
| fetch / pull 网络失败 | 中止提交，不得在「不知是否落后」时 commit |
| 仍有冲突标记或 rebase/merge 未结束 | 中止提交 |
| 已落后远程却未 rebase 完成 | 中止提交 |

### 3.5 禁止借口

| 借口 | 处理 |
| --- | --- |
| 改动很小不用拉 | 改动大小与是否落后无关，先拉 |
| 刚才 / 早上拉过了 | 每次准备 commit 前重新 fetch |
| 先提交再拉 | 顺序写死：先同步，再 commit |
| 有冲突先把本地提交保住 | 冲突未清零禁止新 commit |
| 远程大概没人推 | 必须 fetch，不许猜 |
| 用 force push 顶掉远程 | 禁止用强推代替拉取与消冲突 |

## 4. 安全写法（命令注入防护）

`git commit -m "..."` 会对双引号内内容做 shell 展开。出现反引号或 `$(...)` 时，禁止直接使用双引号形式。

### 4.1 推荐：消息文件提交（优先）

```bash
git commit -F /tmp/commit-msg.txt
```

```bash
cat > /tmp/commit-msg.txt <<'EOF'
feat: 示例提交说明

- 修改点 A
- 修改点 B
EOF
git commit -F /tmp/commit-msg.txt
```

### 4.2 允许：单引号提交

```bash
git commit -m 'feat: 支持 runConcurrent'
```

前提：message 内无单引号字符。

### 4.3 禁止：双引号直接携带反引号

```bash
git commit -m "feat: run `build-tool`"
```

上例存在命令替换风险。

### 4.4 兜底：转义（不推荐）

```bash
git commit -m "feat: run \`build-tool\`"
```

## 5. Stage 级敏感扫描（强制）

同时扫描：
- `git diff --cached`
- `git diff --cached --name-only`

### 5.1 禁止提交文件

`.env*`、`*.pem`、`*.key`、`*.p12`、`*.pfx`、`*.jks`、`*.keystore`、`*.sql`（真实数据）、`*.dump`、`*.sqlite`、`*.xlsx`、`*.csv`（敏感表）、`*.log`、`pgdata/`、`cache/*.json`。

### 5.2 禁止内容片段（示例）

`sk-` 开头 API Key、`AKIA` 开头 AWS Key、`ghp_` GitHub Token、`password=...`、`token=...`、`secret=...`、明文数据库连接串、私钥头、`IP:端口`、`ssh user@ip`。

### 5.3 例外

`.env.example`、环境变量读取方式、`localhost`/`127.0.0.1` 示例连接串可保留。

### 5.4 处理失败

1. 立即停止。
2. 输出 `文件名:行号:命中片段`。
3. 给出修复建议（`.gitignore`、改环境变量、替换占位符）。
4. 用户确认后继续；用户强制提交时，message body 追加：
   - `GIT-SECURITY: 用户已确认提交此内容`

## 6. 变更范围与提交拆分

先执行 `git diff --cached`，明确：修改了哪些模块、影响边界、是否一次可归因。

若单条 message 无法在 `subject` 中清晰表达，必须拆分 commit。

## 7. Commit Scope

Scope 由 AI 根据变更模块与项目语义自行决定，保持与现有提交习惯一致且可读。

- 单模块改动：优先加 scope，名称贴近主改动模块（如 `eui` / `backend` / `cli` 等）。
- 跨模块改动：可不带 scope。
- 无法稳定归类：短期使用无 scope，避免强行造新约束。

## 8. Commit Message 规则

格式：

`<type>(<scope>): <subject>`

或

`<type>: <subject>`

或

`<type>!: <subject>`

或

`<type>(<scope>)!: <subject>`

`type` 限定为：`feat`、`fix`、`refactor`、`chore`、`docs`、`test`、`perf`、`style`、`ci`。

`subject` 规则：

- 中文、动宾短语。
- ≤72 字符。
- 不用句号、不用“了”。
- 不得含 emoji。
- 可选 body 仅说明 why，不要复述 what。
- 破坏性变更：`feat!:` / `fix!:`（带 scope 时写成 `feat(<scope>)!:` / `fix(<scope>)!:`） + `BREAKING CHANGE: ...`

## 9. AI 署名与生成声明治理

commit 的 subject、body、footer、trailer 中禁止出现任何形式的 AI 署名或生成声明。AI 应自行判断：凡由 AI 工具（Claude、ChatGPT、GPT、Copilot、Cursor、Gemini、Llama、LLM 等）生成或参与撰写的署名、尾随声明、自动生成标记，均不得写入 commit message。

包括但不限于：

- `Co-Authored-By: <AI 名称> <noreply@...>`（任何 AI 产品 + 邮箱组合）
- `Generated with Claude Code` / `Generated with ...`（任何"由 XX 生成"声明）
- 含 AI 产品名的署名行（Claude、ChatGPT、GPT、Copilot、Cursor、Gemini、LLM 等）
- AI 平台noreply 邮箱（noreply@anthropic.com、noreply@openai.com 等）

`git commit -m "..."` 不得附带 AI 署名 trailer。

> PreToolUse hook `pre-git-commit-ai-signature-check.sh` 会在 commit message 中检出 Co-Authored-By / Generated with 等 AI 署名模式时硬拦截（exit 2），规则约束 + 工程兜底双保险。

## 10. 参考示例

- `feat(eui): 添加 Image 组件懒加载支持`
- `refactor(backend): 提取分页逻辑为共享工具`
- `fix(eui)!: 重构 EDialog open 属性为 v-model:open`
  - `BREAKING CHANGE: EDialog 不再接受 visible 属性，请改用 v-model:open`
