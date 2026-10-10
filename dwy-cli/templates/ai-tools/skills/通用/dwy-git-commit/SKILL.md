---
name: dwy-git-commit
description: "准备 git commit、写 commit message、处理 git pull / rebase 冲突、做提交前检查时必须使用（即使用户没说 skill 名）。先 fetch 再 rebase，冲突未清零不提交；暂存区不进密钥；message 用约定 type；删掉 AI 署名。只改代码、不提交时不要用。"
---

# Git 提交

本次任务包含提交、commit message、`git pull` / rebase 冲突、提交前检查时读本 skill。只改代码、不提交时不用。

没有 skill 的工具只看 `rules/开发流程/dwy-git-commit.md`。和那份短 rule 冲突时以本 skill 为准。

任一步不通过：中止提交。项目按多人协作处理，本地未基于最新远程提交前，禁止产生新 commit。

## 1. 顺序

1. 拉取远程并处理完全部冲突
2. 安全写法检查
3. 暂存区敏感扫描
4. 变更范围确认
5. Scope 与 message 格式
6. 删掉 AI 署名

## 2. 先同步远程

未完成同步、冲突未清零：禁止 `git commit`。

先 fetch，再 rebase。工作区有未提交改动时带 `--autostash`，禁止为了拉代码丢弃本地改动。

```bash
git fetch origin
git pull --rebase --autostash
```

当前分支已设置上游时，上面两条即可。未设置上游但远程存在同名分支：

```bash
git fetch origin
git pull --rebase --autostash origin "$(git branch --show-current)"
```

无 `origin` 时，对实际存在的 remote 做同等操作。

冲突出现后：

1. 逐处消解 `<<<<<<<` / `=======` / `>>>>>>>`。
2. `git add` 已解决文件。
3. rebase 进行中用 `git rebase --continue`，不要另开 `git commit` 顶掉 rebase。
4. stash 弹出后再次冲突，同样消解并 `git add`。
5. 全库无冲突标记、无未结束的 rebase / merge，再做后面的检查。

禁止用 `git rebase --abort` / `git merge --abort` 躲冲突后直接提交。

只有这两种情况可以跳过同步，并在回复里写明原因：仓库没有任何 remote；`git fetch` 后当前分支在所有 remote 上都不存在同名分支。

| 情况 | 处理 |
| --- | --- |
| fetch / pull 网络失败 | 中止提交 |
| 仍有冲突标记或 rebase / merge 未结束 | 中止提交 |
| 已落后远程却未 rebase 完成 | 中止提交 |
| 改动很小、刚才拉过、先提交再拉、猜远程没人推 | 仍要先 fetch |
| 用 force push 顶掉远程 | 禁止用强推代替拉取 |

## 3. 命令写法

`git commit -m "..."` 会对双引号内容做 shell 展开。出现反引号或 `$(...)` 时，禁止直接使用双引号。

优先把 message 写进文件：

```bash
git commit -F /tmp/commit-msg.txt
```

message 内无单引号时，可以用单引号：`git commit -m 'feat: 支持 runConcurrent'`。

## 4. 暂存区敏感扫描

同时看 `git diff --cached` 和 `git diff --cached --name-only`。

禁止提交：`.env*`、`*.pem`、`*.key`、`*.p12`、`*.pfx`、`*.jks`、`*.keystore`、真实数据的 `*.sql`、`*.dump`、`*.sqlite`、敏感表的 `*.xlsx` / `*.csv`、`*.log`、`pgdata/`、`cache/*.json`。

禁止内容：`sk-` 开头的 API Key、`AKIA` 开头的 AWS Key、`ghp_` GitHub Token、`password=`、`token=`、`secret=`、明文数据库连接串、私钥头、`IP:端口`、`ssh user@ip`。

`.env.example`、环境变量读取方式、`localhost` / `127.0.0.1` 示例连接串可以留。

命中后停止，输出 `文件名:行号:命中片段` 和改法（`.gitignore`、改环境变量、换占位符）。用户确认后才能继续。用户强制提交时，message body 追加 `GIT-SECURITY: 用户已确认提交此内容`。

## 5. 范围与 message

先看 `git diff --cached`。一条 subject 说不清这次改动，就拆 commit。

格式：`<type>(<scope>): <subject>`，或 `<type>: <subject>`。破坏性变更写成 `feat!:` / `fix!:`（有 scope 时 `feat(<scope>)!:`），body 加 `BREAKING CHANGE: ...`。

`type` 只使用：`feat`、`fix`、`refactor`、`chore`、`docs`、`test`、`perf`、`style`、`ci`。

Scope 按变更模块和仓库现有习惯。单模块优先加 scope。跨模块可以不加。归不稳时宁可不加，不新造一套 scope。

`subject`：中文动宾短语，不超过 72 字符，不用句号，不含 emoji。body 只写为什么。

示例：

- `feat(eui): 添加 Image 组件懒加载支持`
- `refactor(backend): 提取分页逻辑为共享工具`
- `fix(eui)!: 重构 EDialog open 属性为 v-model:open`

## 6. AI 署名

提交前看完整的 commit 命令和 message 文件。有 AI 署名就删掉再提交。环境会自己往命令里塞署名（例如 `Co-authored-by: Cursor <cursoragent@cursor.com>`），看见就去掉。

hook 会拦：`Co-Authored-By:`、`Generated with`、Claude / ChatGPT / GPT / Copilot / Cursor 等产品名、`noreply@anthropic.com`、`noreply@openai.com`。

名单里没有的，提交前自己判断。一行只要是在给 AI 工具、模型、Agent、机器人署名，或声明这段提交由 AI 生成、协助、代写，就删。人写的正常说明留着。

不要加 `--trailer`，不要多一条 `-m` 放署名，不要把署名留在 `-F` 的文件里。hook 拦住之后删掉再交，不绕过 hook。
