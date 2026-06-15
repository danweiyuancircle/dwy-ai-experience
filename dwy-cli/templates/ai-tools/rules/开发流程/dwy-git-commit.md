---
description: Git Commit 规范（提交安全、敏感扫描、Scope、消息规范、AI 署名治理）
---

# Git Commit 规范（强制）

## 1. 适用范围

适用于所有 Git 提交流程，覆盖：

- `git add`
- `git commit`
- 为提交生成或校验 commit message 的场景

任一步骤不通过：中止当前提交流交付流程。

## 2. 执行顺序（硬约束）

1. 安全写法检查
2. Stage 级敏感扫描
3. 变更范围确认
4. Scope 与 message 格式校验
5. AI 署名与生成声明校验

## 3. 安全写法（命令注入防护）

`git commit -m "..."` 会对双引号内内容做 shell 展开。出现反引号或 `$(...)` 时，禁止直接使用双引号形式。

### 3.1 推荐：消息文件提交（优先）

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

### 3.2 允许：单引号提交

```bash
git commit -m 'feat: 支持 runConcurrent'
```

前提：message 内无单引号字符。

### 3.3 禁止：双引号直接携带反引号

```bash
git commit -m "feat: run `build-tool`"
```

上例存在命令替换风险。

### 3.4 兜底：转义（不推荐）

```bash
git commit -m "feat: run \`build-tool\`"
```

## 4. Stage 级敏感扫描（强制）

同时扫描：
- `git diff --cached`
- `git diff --cached --name-only`

### 4.1 禁止提交文件

`.env*`、`*.pem`、`*.key`、`*.p12`、`*.pfx`、`*.jks`、`*.keystore`、`*.sql`（真实数据）、`*.dump`、`*.sqlite`、`*.xlsx`、`*.csv`（敏感表）、`*.log`、`pgdata/`、`cache/*.json`。

### 4.2 禁止内容片段（示例）

`sk-` 开头 API Key、`AKIA` 开头 AWS Key、`ghp_` GitHub Token、`password=...`、`token=...`、`secret=...`、明文数据库连接串、私钥头、`IP:端口`、`ssh user@ip`。

### 4.3 例外

`.env.example`、环境变量读取方式、`localhost`/`127.0.0.1` 示例连接串可保留。

### 4.4 处理失败

1. 立即停止。
2. 输出 `文件名:行号:命中片段`。
3. 给出修复建议（`.gitignore`、改环境变量、替换占位符）。
4. 用户确认后继续；用户强制提交时，message body 追加：
   - `GIT-SECURITY: 用户已确认提交此内容`

## 5. 变更范围与提交拆分

先执行 `git diff --cached`，明确：修改了哪些模块、影响边界、是否一次可归因。

若单条 message 无法在 `subject` 中清晰表达，必须拆分 commit。

## 6. Commit Scope

Scope 由 AI 根据变更模块与项目语义自行决定，保持与现有提交习惯一致且可读。

- 单模块改动：优先加 scope，名称贴近主改动模块（如 `eui` / `backend` / `cli` 等）。
- 跨模块改动：可不带 scope。
- 无法稳定归类：短期使用无 scope，避免强行造新约束。

## 7. Commit Message 规则

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

## 8. AI 署名与生成声明治理

commit 的 subject、body、footer、trailer 中禁止出现：

- `Co-Authored-By: Claude ...`
- `Generated with Claude Code`
- `Generated with ...`
- `Claude`、`ChatGPT`、`GPT`、`Copilot`、`Cursor`、`AI`、`LLM`
- `noreply@anthropic.com`、`noreply@openai.com`

`git commit -m "..."` 不得附带 AI 署名 trailer。

## 9. 参考示例

- `feat(eui): 添加 Image 组件懒加载支持`
- `refactor(backend): 提取分页逻辑为共享工具`
- `fix(eui)!: 重构 EDialog open 属性为 v-model:open`
  - `BREAKING CHANGE: EDialog 不再接受 visible 属性，请改用 v-model:open`
