---
name: dwy-sdk-spec
description: "通用 SDK 发布前安全检查——任何 SDK 对外发布（PyPI / npm / 私有源 / 直接交付，渠道不限）前都应先过这一关。查三类风险：①接口注释是否泄露后端实现（内网域名、数据库表名、Redis key、内部服务名、员工邮箱、JIRA 链接、SQL 语句）；②商业版 SDK 源码是否被保护（Python 用 Cython 编译 .so、JS 用 tsup/rollup minify + files 白名单）；③发布产物是否夹带隐藏敏感文件（.py 源码 / .map source map / .env / .npmrc / tsbuildinfo / __pycache__ 等）。跨项目复用：首次进入新项目用 AskUserQuestion 问商业版还是开源版，缓存到 <project_root>/.dwy/sdk-spec/config.json，下次自动按规则检查。涉及以下任何场景必须使用此 skill：用户说「检查 SDK」「SDK 发版前检查」「SDK 注释脱敏」「SDK 接口规范」「发布前安全检查」「SDK 源码泄露检查」「商业版 SDK 打包」「Cython 编译 .so」「打包前体检」「.gitignore 漏了什么」「npm pack 看看包里有什么」「重设 SDK 版本类型」时。注：本 skill 只做发布前安全检查闸门，不执行发版流程（发版编排走 dwy-publish，会在发布前主动调用本检查）。"
---

# dwy-sdk-spec — SDK 接口规范与发布安全检查

防三类风险：接口注释泄露后端实现 / 商业版 SDK 源码被还原 / 发布产物夹带隐藏敏感文件。

**适用范围**：任何 SDK 对外发布前的通用安全闸门，与发布渠道无关——PyPI / npm / 私有源 / 直接打包交付都先过这一关。发 PyPI 只是其中一种渠道，不是触发前提。检查通过后，通用发版流程（测试 / bump / changelog / tag / publish）走 `dwy-publish`；含 C 扩展需跨平台 wheel 的走 `dwy-github-action-publish`。

## 何时触发

下列任何场景**必须**用此 skill，不要直接 `npm publish` / `python -m build` / `twine upload`：

- 用户说「检查 SDK」「SDK 发版前检查」「SDK 接口规范」
- 用户说「准备发布 SDK」（PyPI / npm / 私有源等任意渠道）「发布前体检」「打包前检查」
- 用户说「SDK 注释脱敏」「SDK 源码泄露检查」「.gitignore 漏了什么」
- 用户说「商业版 SDK 打包」「Cython 编译 .so」「npm 包混淆」
- 用户说「npm pack 看看包里有什么」「dist 目录看一下」
- 用户说「重设 SDK 版本类型」「换商业 / 开源版本」

## 工作流程 0：项目识别与配置（必走）

skill 跨项目复用。每次执行流程 A/B/C 前先确保当前项目的配置就绪。

### 缓存文件格式

路径：`<project_root>/.dwy/sdk-spec/config.json`（写项目内，扁平结构，不存绝对路径）

```json
{
  "version": "1",
  "edition": "commercial",
  "languages": ["python", "js"],
  "sdk_paths": {
    "python": ["backend"],
    "js": ["frontend/eui", "frontend/ekit"]
  },
  "configured_at": "2026-05-18T12:34:56Z"
}
```

- `edition` 必填，只能是 `commercial` 或 `opensource`
- `languages` / `sdk_paths` 自动探测，`sdk_paths` 是**相对项目根的相对路径**
- 配置随项目走、不存绝对路径；`.dwy/` 是本机判断缓存，提醒用户加进 `.gitignore`

### 读取流程

```bash
SKILL_DIR="$(dirname "$0")"   # 实际跑时 Claude 用 SKILL.md 所在目录拼 scripts/
PROJECT_PATH=$(pwd)
CONFIG=$(bash "$SKILL_DIR/scripts/init_config.sh" get "$PROJECT_PATH")
```

- 输出非 `null` → 已配置，提取 `edition` / `languages` / `sdk_paths`，先做**路径校验**（见下），再跳到对应流程
- 输出 `null` → 走「首次配置」

### 路径校验（应对 SDK 目录改名）

`sdk_paths` 存相对路径，SDK 子目录改名（如 `backend`→`core`）后缓存会指向已不存在的目录。get 返回非 `null` 后，逐个检查 `sdk_paths` 里的相对目录在 `$PROJECT_PATH` 下是否存在：

```bash
for d in $(jq -r '.sdk_paths[][]' <<< "$CONFIG"); do
  [[ -d "$PROJECT_PATH/$d" ]] || echo "MISSING: $d"
done
```

- 全部存在 → 直接用缓存
- 有 `MISSING` → 警告用户「缓存的 SDK 路径已失效」，跑 `detect_sdk.sh` 重新探测，再用 `init_config.sh set` 覆盖更新（`edition` 沿用旧值），然后继续

### 首次配置流程

1. 跑 `bash scripts/detect_sdk.sh "$PROJECT_PATH"` 探测语言：
   - 看到 `pyproject.toml`（含 `[project]` 段）或 `setup.py` → Python SDK
   - 看到 `package.json`（含 `main` / `exports` / `module` 字段）→ JS SDK
   - monorepo 递归找子包（限 2 层深度），输出 JSON：

     ```json
     {"python": ["backend"], "js": ["frontend/eui", "frontend/ekit"]}
     ```

   - 都没找到 → 报错「当前目录不是 SDK 项目」，让用户确认 `pwd` 是否在项目根

2. **AskUserQuestion 问商业 / 开源**（必问，不能默认）：

   - 标题：「当前项目 SDK 是商业版还是开源版？」
   - header：「SDK 版本」
   - 选项：
     - 「商业版（严格检查）」— 必须 Cython 编译 .so / npm 必须 minify + 白名单 files / 注释脱敏 + 打包白名单
     - 「开源版（宽松检查）」— 仅做注释脱敏 + 打包黑名单（防 .env / .npmrc / .map 漏出）
   - 不提供默认值，等用户选

3. 写入缓存：

   ```bash
   bash "$SKILL_DIR/scripts/init_config.sh" set "$PROJECT_PATH" "$EDITION" "$LANGUAGES_JSON" "$SDK_PATHS_JSON"
   ```

### 重设配置流程

用户说「换商业 / 开源版本」「重设 SDK 版本类型」：

```bash
bash "$SKILL_DIR/scripts/init_config.sh" reset "$PROJECT_PATH"
```

然后重新走首次配置。

## 工作流程 A：接口注释脱敏检查（商业版+开源版都跑）

### 目的

SDK 对外的 docstring / JSDoc / TSDoc **只写功能含义、入参格式、返回值、异常**，不写实现细节。常见泄露：内网域名、数据库表名、Redis key、内部服务名、SQL 语句、员工邮箱、JIRA 工单号。

### 执行

```bash
bash "$SKILL_DIR/scripts/check_comments.py" "$PROJECT_PATH" --sdk-paths "$SDK_PATHS_JSON"
```

脚本输出 JSON 数组，每项：

```json
{"file": "backend/src/dwyeapi/security.py", "line": 42, "pattern": "internal-domain", "match": "api.internal.corp.com", "context": "Connect to https://api.internal.corp.com/v2"}
```

### 违规处理

逐项展示给用户：
- 引用 `references/sensitive-patterns.md` 给出正例 / 反例对照
- 建议修复方案（删除 / 替换为公开描述）
- 误报场景 → 在该行后加 `# sdk-spec: ignore` 注释豁免（脚本会跳过）

**禁止**直接帮用户改源码，只输出修复建议清单让用户决策。

## 工作流程 B：商业版打包配置检查（仅 edition=commercial）

### Python SDK 分支

跑下面 4 项静态检查（不打包）：

```bash
# 1. pyproject.toml 是否含 Cython ext_modules
grep -q 'cython\|ext_modules' "$PROJECT_PATH/pyproject.toml"

# 2. 核心模块（_ 开头）是否已编译为 .so
find "$PROJECT_PATH/<python_sdk_path>" -name '_*.so' -type f

# 3. MANIFEST.in 是否含全局排除
grep -E 'global-exclude.*\*\.py' "$PROJECT_PATH/MANIFEST.in"

# 4. .gitignore 是否含必要项
grep -E '^\*\.so$|^build/$|^dist/$|^\*\.egg-info' "$PROJECT_PATH/.gitignore"
```

缺哪条 → 引用 `references/python-commercial-guide.md` 给修复片段，提供 `assets/python-commercial.gitignore` 和 `assets/python-commercial-MANIFEST.in` 让用户 cp 到项目根（用 AskUserQuestion 让用户确认）。

### JS SDK 分支

跑下面 4 项静态检查：

```bash
# 1. package.json 有 files 白名单且不含 src/ tests/
jq -e '.files | length > 0 and (contains(["src/"]) or contains(["src"])) | not' "$PROJECT_PATH/<js_sdk_path>/package.json"

# 2. 打包工具配置 minify + 无 sourcemap
grep -E 'minify.*true|legalComments.*none|sourcemap.*false' "$PROJECT_PATH/<js_sdk_path>/tsup.config.*"

# 3. dist/ 下没有 .map 文件
find "$PROJECT_PATH/<js_sdk_path>/dist" -name '*.map' -type f 2>/dev/null

# 4. .gitignore 含 .env / *.tsbuildinfo
grep -E '\.env|\.tsbuildinfo' "$PROJECT_PATH/.gitignore"
```

缺哪条 → 引用 `references/js-commercial-guide.md`，提供 `assets/js-commercial.npmignore` 和 `assets/files-whitelist-snippet.json`。

## 工作流程 C：发布前文件清单审计

**商业版严格 / 开源版宽松**，规则不同：

| 版本 | Python 策略 | JS 策略 |
|---|---|---|
| commercial | 白名单：只允许 `.so` `.dist-info/` `.pyi` `.typed` `LICENSE` `README.md` 与必要资源 | 白名单：只允许 `dist/` `README.md` `LICENSE` `package.json` |
| opensource | 黑名单：禁 `__pycache__/` `*.pyc` `.mypy_cache` `*.egg-info/` `.env*` `*.pdb` | 黑名单：禁 `.env*` `.npmrc` `*.map` `*.tsbuildinfo` `tsconfig.json` `.git*` `node_modules` |

### Python 执行

```bash
bash "$SKILL_DIR/scripts/check_python_publish.sh" "$PROJECT_PATH/<python_sdk_path>" --edition "$EDITION"
```

脚本内部跑 `python -m build`（生成 wheel 到临时目录），`unzip -l dist/*.whl` 列文件，按 edition 白名单 / 黑名单断言。结束自动清理临时 dist。

### JS 执行

```bash
bash "$SKILL_DIR/scripts/check_js_publish.sh" "$PROJECT_PATH/<js_sdk_path>" --edition "$EDITION"
```

脚本内部跑 `npm pack --dry-run --json` 拿包内文件列表，按 edition 断言。不实际产生 .tgz。

### 输出

每项违规：`<文件名>  [规则: <白/黑名单条目>]  → 建议: <修复方案>`

修复方案：
- 多余文件 → 加到 `package.json` `files` 白名单外，或加到 `MANIFEST.in` `global-exclude`
- 缺少文件 → 检查打包脚本是否漏跑

**禁止**直接帮用户改配置文件，输出建议清单让用户决策。

## 错误处理速查

| 情况 | 处理 |
|---|---|
| 脚本说命中敏感词但是误报 | 该行后加 `# sdk-spec: ignore`（Python）或 `// sdk-spec: ignore`（JS/TS）行内豁免 |
| 商业版但项目特殊不用 Cython（如纯接口包） | 跟用户确认；要长期跳过 Python 商业打包检查 → `bash scripts/init_config.sh reset "$(pwd)"` 重选「开源版」，或单次跳过流程 B |
| 想换商业 / 开源版本 | `bash scripts/init_config.sh reset "$(pwd)"` 然后重触发 skill 重问 |
| `detect_sdk.sh` 没找到 SDK 但项目确实是 | 让用户手动指定 `--sdk-paths '{"python":["src/mypkg"]}'`，跳过自动探测 |
| `python -m build` 失败 | 报告原因给用户，建议先 `pip install build`；不强制执行流程 C，可仅做流程 A+B |
| `npm pack --dry-run` 失败 | 多半是 `npm install` 没跑或 `package.json` 缺字段，让用户先修复，重跑 |
| 缓存文件损坏（jq 解析失败） | 提示用户备份原文件后删除 `<project_root>/.dwy/sdk-spec/config.json`，重新走首次配置 |
| 缓存的 SDK 路径失效（目录改名/删除） | 走「路径校验」：警告后跑 `detect_sdk.sh` 重探测 + `set` 覆盖更新 |

## 跨项目约束

skill 文件**零绝对路径**。装到任何机器上首次用时自动走流程 0。

需要用户机器满足：
1. 装了 `jq`（解析缓存 JSON）
2. Python 项目：装了 `python` 与 `build` 包（流程 C 用）
3. JS 项目：装了 `npm` 与 `node`（流程 C 用）
4. 缓存文件写项目内 `<project_root>/.dwy/sdk-spec/config.json`，是本机判断缓存，提醒用户加进 `.gitignore`，不入版本库

## 安全约束

- skill 不存任何 token / 凭证 / 私钥
- skill 不动 `~/.pypirc` / `~/.npmrc`
- 脚本只做本地读 + 本地写 `<project_root>/.dwy/sdk-spec/`
- 不静默修改任何源文件 / 配置文件，所有改动建议输出给用户决策
- 不实际发布到 PyPI / npm，流程 C 全部使用 `--dry-run` 或临时目录
- 检查通过 ≠ 安全保证，最终发布前用户必须人工 review `npm pack --dry-run` 输出
