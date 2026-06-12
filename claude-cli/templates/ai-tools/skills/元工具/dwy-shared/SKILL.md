---
name: dwy-shared
description: "管理 dwy-shared 模板仓库与 dwy CLI 工具。功能 1：把本机已有的 skill/rule/hook/command 文件加进 dwy-shared 仓库时，自动读现有分类目录、推荐归位、AskUserQuestion 确认后 cp/git mv + commit + push 到 Gitee，让别的项目用 dwy claude sync 拉到。功能 2：管理 dwy npm CLI（create-dwy）的安装/更新/卸载/版本查询/CDN 延迟应急。涉及以下任何场景必须使用此 skill：用户说「加 X 到 dwy-shared」「在 dwy-shared 新增 skill/rule/hook/command」「dwy 仓库整理」「dwy-shared 仓库管理」「换 dwy-shared 仓库路径」「重设 dwy-shared」「升级/装/卸/重装 dwy CLI」「dwy 拉不到最新版」「create-dwy 怎么装」「dwy --version 显示旧版」「dwy CDN 没传播」。"
---

# dwy-shared 仓库管理

管理 dwy-shared 模板仓库内 skills/rules/hooks/commands 的入库归类，以及 dwy CLI 的本机生命周期。

## 何时触发

下列任何场景**必须**用此 skill，不要直接动手：

- 用户给一个本机文件路径，说要加到 dwy-shared 仓库
- 用户说「在 dwy-shared 仓库新增 skill/rule/hook/command」
- 用户说「dwy 仓库整理 / dwy-shared 仓库管理」
- 用户说「升级/装/卸/重装 dwy CLI」
- 用户说「dwy 拉不到最新版 / dwy --version 是旧版」
- 用户说「换 dwy-shared 路径 / 重设 dwy-shared / dwy-shared 仓库挪了」

## 工作流程 0：仓库位置配置（必走）

skill 与 dwy-shared 仓库深度绑定但**不硬编码路径**。每次执行流程 A/B 前先确保缓存就绪。

### 缓存文件格式

路径：`~/.config/dwy-shared/repo.json`

```json
{
  "repo_path": "/绝对/路径/到/dwy-shared",
  "git_url": "https://gitee.com/snailyuanyuan/dwy-shared.git",
  "configured_at": "2026-05-18T12:34:56Z"
}
```

### 读取与校验

```bash
CONFIG="$HOME/.config/dwy-shared/repo.json"
if [ -f "$CONFIG" ]; then
  REPO_PATH=$(jq -r .repo_path "$CONFIG" 2>/dev/null)
  if [ -n "$REPO_PATH" ] && [ -d "$REPO_PATH/.git" ] && [ -d "$REPO_PATH/claude-cli/templates/ai-tools" ]; then
    echo "OK: $REPO_PATH"
  else
    echo "INVALID"
  fi
else
  echo "MISSING"
fi
```

- `OK` → 继续后续流程
- `INVALID` 或 `MISSING` → 走「首次配置」

### 首次配置流程

1. 告知用户：「我需要知道 dwy-shared 仓库在你本机的 clone 位置」
2. AskUserQuestion 问：「已经 clone 过 dwy-shared 仓库了吗？」
   - **已 clone**：让用户告诉绝对路径（用 AskUserQuestion 的 Other 自由输入，或直接让用户回消息贴路径）
   - **未 clone**：输出 git URL 让用户先 clone：

     ```
     git clone https://gitee.com/snailyuanyuan/dwy-shared.git <你想放的位置>
     ```

     然后告诉路径
3. 拿到路径后，**严格校验**：
   - `test -d "$PATH"` 路径存在
   - `test -d "$PATH/.git"` 是 git 仓库
   - `git -C "$PATH" remote -v | grep -q dwy-shared` remote 指向 dwy-shared
   - `test -d "$PATH/claude-cli/templates/ai-tools"` 含特征目录
4. 全部通过 → 写缓存：

   ```bash
   mkdir -p "$HOME/.config/dwy-shared"
   cat > "$HOME/.config/dwy-shared/repo.json" <<EOF
   {
     "repo_path": "$PATH",
     "git_url": "https://gitee.com/snailyuanyuan/dwy-shared.git",
     "configured_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
   }
   EOF
   ```

5. 任一校验失败 → 列出失败项让用户重输

### 修改路径流程

用户说「换 dwy-shared 路径」「dwy-shared 挪了」「重设 dwy-shared」：

1. 读现有 config，告诉用户「当前缓存路径是 X」
2. 走首次配置流程，覆盖 config

## 工作流程 A：往仓库加新模板

### 步骤 1：拿仓库路径

执行流程 0 的读取与校验。无效 → 先走首次配置，配完回到这里。

不依赖 cwd —— 用户在 `/tmp` / `~/Desktop` 都行。后续命令统一用绝对路径，**不要 cd 到仓库**（避免污染用户 cwd）。

### 步骤 2：识别类型

根据用户给的源（绝对路径）判断属于哪类模板：

- **skill**：源是目录且含 `SKILL.md` 文件
- **rule**：源是 `.md` 文件，且 frontmatter 含 `paths:` 字段，或文件名形如 `dwy-<topic>-<aspect>.md`
- **hook**：源是 `.sh` 脚本，或文件名形如 `pre-*` / `post-*`
- **command**：源是 `.md` 文件，文件名是单词形式（如 `lint.md`、`deploy.md`），用作斜杠命令

歧义时用 AskUserQuestion 让用户选 skill/rule/hook/command。

### 步骤 3：读现有分类 + 准备推荐上下文

```bash
TYPE_DIR="$REPO_PATH/claude-cli/templates/ai-tools/<type>"
for cat in "$TYPE_DIR"/*/; do
  echo "=== $(basename "$cat") ==="
  # 读分类下第一个样例的 description 行（前 100 字）
  first_sample=$(find "$cat" -name '*.md' | head -1)
  test -n "$first_sample" && grep -m1 "^description" "$first_sample" | head -c 100
done
```

得到「现有分类 + 各分类的代表性描述」上下文。

### 步骤 4：推荐归位

读源文件的 description / 内容前 500 字，结合现有分类样例，推荐 1 个最匹配分类。

如果新文件明显不属于任何现有分类（如全新技术栈），**主动建议新建分类**，提一个名字（中文优先，与现有风格一致：技术栈用英文 `Flutter`/`Vue`，业务域用中文 `运维发布`/`基础库`）。

### 步骤 5：AskUserQuestion 确认分类

选项：
- 推荐分类（标记「推荐」放第一位）
- 其他现有分类
- 「新建分类」（让用户在 Other 输入分类名）

### 步骤 6：执行文件操作

```bash
TARGET_DIR="$REPO_PATH/claude-cli/templates/ai-tools/<type>/<category>"
mkdir -p "$TARGET_DIR"

# 源在仓库外：cp
cp -r <源> "$TARGET_DIR/<name>"

# 源在仓库内（如从其他分类移动）：git mv
git -C "$REPO_PATH" mv <仓库内相对路径> <new-相对路径>
```

**冲突处理**：目标已存在 → AskUserQuestion 让用户选「覆盖 / 改名 / 取消」。

### 步骤 7：staged + 显示 diff

```bash
git -C "$REPO_PATH" add <精准路径>
git -C "$REPO_PATH" status --short
git -C "$REPO_PATH" diff --cached --stat
```

把 status + diff stat 输出给用户看，让他看到将提交什么。

**禁止**用 `git add -A` 或 `git add .`，避免误捎带用户的在途工作。

### 步骤 8：生成 commit message

按项目 `CLAUDE.md` 中 Git Commit Scope 规范：
- scope: `cli`
- type: `feat`（新模板）/ `fix`（修复模板）/ `docs`（仅文档）
- subject: 中文动宾短语 ≤72 字符
- **禁** AI 署名 / Co-Authored-By trailer

模板：
- `feat(cli): 新增 <name> skill 到 <分类> 分类`
- `feat(cli): 新增 <name> rule 到 <分类> 分类`
- `feat(cli): 新增 <分类>/<name> hook`

### 步骤 9：AskUserQuestion 确认 commit + push

选项：
- 「✓ 确认 commit + push」
- 「修改 commit message」（用户改完再 commit）
- 「✗ 取消」（保留 staged 状态让用户手动处理）

### 步骤 10：执行

```bash
git -C "$REPO_PATH" -c commit.gpgsign=false commit -m "$MSG"
git -C "$REPO_PATH" push origin master
```

### 步骤 11：完成提示

告知用户：
- ✓ 已 push 到 Gitee
- 更新当前仓库的 `templates/ai-tools/` 后，发布新的 `create-dwy` 版本；其他项目升级 CLI 后即可使用新模板
- 提醒：如果对方 dwy CLI <0.12.0，必须先升级 CLI 才能识别分类目录结构

## 工作流程 B：dwy CLI 管理

固定命令封装：

| 用户意图 | 命令 |
|---|---|
| 安装 / 升级到最新 | `npm i -g create-dwy@latest --registry=https://registry.npmjs.org/ --prefer-online` |
| 升级到指定版本 | `npm i -g create-dwy@<version> --registry=https://registry.npmjs.org/ --prefer-online` |
| 卸载 | `npm uninstall -g create-dwy` |
| 查本地版本 | `dwy --version` |
| 查 npm 上最新版 | `npm view create-dwy version` |
| 应急重装（cache 损坏） | `npm cache clean --force && npm i -g create-dwy@latest --registry=https://registry.npmjs.org/ --prefer-online` |

### CDN 延迟应急

如果用户刚 publish 完，跑 `npm view create-dwy version` 还显示旧版 / `npm i` 报 `ETARGET` —— 这是 npm CDN 传播延迟（30s ~ 几分钟），**不是失败**。

直接打主 registry 旁路 CDN：

```bash
curl -s https://registry.npmjs.org/create-dwy | jq '."dist-tags".latest'
```

如果显示是新版，等 30s 重试 `npm i` 或加 `--prefer-online --registry=https://registry.npmjs.org/`。

## 错误处理速查

| 情况 | 处理 |
|---|---|
| 缓存路径不存在 | 走首次配置 |
| 缓存路径不是 git 仓库 / 不含特征目录 | 提示用户重设，走修改路径流程 |
| 源文件不存在 | 报错让用户确认路径 |
| 目标已存在同名文件/目录 | AskUserQuestion：覆盖 / 改名 / 取消 |
| 工作区有其他 uncommitted 改动 | 提示用户先 stash 或 commit 现有改动，避免误提（用 `git status --porcelain` 检测） |
| git push 鉴权失败 | 提示配 git credential helper / SSH key，告知不要在 skill 里存任何凭证 |
| git push 非快进失败 | 提示用户先 `git -C "$REPO_PATH" pull --rebase` 再重试 |
| dwy --version 报 command not found | 走流程 B 安装 |

## 跨机器约束

skill 文件**零绝对路径**。换台机器装上后第一次用时自动走首次配置流程。

需要用户机器满足：
1. 装了 `git` / `jq` / `npm`（jq 用于解析缓存 JSON）
2. clone 了 dwy-shared 仓库到任意位置（skill 引导）
3. 对 Gitee origin 有 push 权限
4. 缓存文件 `~/.config/dwy-shared/repo.json` 是机器本地配置，**不**随 skill 文件同步出去

## 安全约束

- skill 不存任何 token / 凭证 / 私钥
- skill 不动 `~/.npmrc` / `~/.git-credentials`
- 仓库路径只存在用户机器本地 `~/.config/dwy-shared/repo.json`
- commit + push 前必须经 AskUserQuestion 确认，不静默推送
