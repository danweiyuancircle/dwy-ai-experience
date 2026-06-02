---
name: dwy-cibuildwheel
description: "用 GitHub Actions + cibuildwheel 把【含 C 扩展 / Cython / .so 编译产物】的 Python 包跨平台 build wheel（linux/macos/windows × x86_64/arm64）并通过 PyPI Trusted Publisher (OIDC) 发布到 PyPI 的避坑指南。仅适用于需要编译 .so 的包；纯 Python 包发 PyPI 不需要本 skill（走 dwy-publish + dwy-sdk-spec）。涵盖 PEP 639 license / cibuildwheel 版本 tag / YAML 冒号转义 / {package} 占位符 / 跨平台 shell 引号 / manylinux 镜像 / 测试阶段 binary 强制 / GitHub runner image 退役（macos-13 已死）等 8 类高频坑。触发条件：编辑或新建含 cibuildwheel 的 .github/workflows/*.yml、pyproject.toml 含 Cython / ext_modules、用户说 'cibuildwheel' / 'build wheel' / '跨平台 wheel' / '.so 跨平台打包' / 'wheel build 失败' / 'macos runner 一直 queued'，或要把含 C 扩展的 Python 包发 PyPI 时。"
---

# dwy-cibuildwheel — Python Cython SDK 跨平台 PyPI 发布避坑

适用场景：含 Cython 编译扩展的 Python 包、跨平台 wheel 分发（linux x86_64/aarch64 + macos x86_64/arm64 + windows AMD64）、GitHub Actions + cibuildwheel + PyPI Trusted Publisher OIDC 发版。

> 定位：本 skill 只解决「含 C 扩展的包怎么用 GitHub Actions 跨平台打 wheel 发 PyPI」的 CI 避坑。通用发版流程（测试 / bump / changelog / tag）走 `dwy-publish`；发布前接口脱敏 / 源码泄露 / 产物审计走 `dwy-sdk-spec`；纯 Python 包不需要本 skill。

**实战来源**：quant-sdk (quantzone) 0.4.0 首发到 PyPI 过程中暴露的 8 类坑，全部沉淀于此。

---

## 8 个高频坑

### 坑 1：PEP 639 license expression 触发 build env 依赖冲突

**症状**（任意平台 build 阶段）：
```
ImportError: Cannot import `packaging.licenses`.
Setuptools>=77.0.0 requires "packaging>=24.2" to work properly.
```

**根因**：`pyproject.toml` 用了 PEP 639 字符串形式 `license = "MIT"`。setuptools 77+ 校验 license expression 时强依赖 `packaging>=24.2`，但跨平台 cibuildwheel 临时 build env 装到老 packaging 时直接撞死。

**修复**：在 `[build-system].requires` 显式锁两个下限：
```toml
[build-system]
requires = [
    "setuptools>=77",
    "packaging>=24.2",
    "wheel",
    "Cython>=3.0.10",
]
build-backend = "setuptools.build_meta"
```

**例外**：还在用老语法 `license = {text = "MIT"}` / `license = {file = "LICENSE"}` 的项目不触发。但 PEP 639 是趋势，建议主动对齐 + 提前锁依赖。

---

### 坑 2：cibuildwheel action 必须用 minor 级或精确 tag

**症状**（workflow 启动几秒就 fail，错误页面提示）：
```
Unable to resolve action `pypa/cibuildwheel@v3`, unable to find version `v3`
```

**根因**：不像 `actions/checkout@v4` 那种 major moving alias，`pypa/cibuildwheel` **只维护 minor 级 moving tag**（`v3.4`）和精确 patch tag（`v3.4.1`），**没有 `v3` 这种 major alias**。

**修复**：
```yaml
- uses: pypa/cibuildwheel@v3.4    # minor moving，自动跟 v3.4.x patch（推荐）
# 或精确锁
- uses: pypa/cibuildwheel@v3.4.1
```

**自检**：改 action 版本前先查实际存在的 tag：
```bash
curl -sL https://api.github.com/repos/pypa/cibuildwheel/git/refs/tags \
  | python3 -c "import sys,json; tags=[r['ref'].replace('refs/tags/','') for r in json.load(sys.stdin)]; print([t for t in tags if t.startswith('v3')][-10:])"
```

通用教训：**不要假设任何 GitHub Action 都有 `v<N>` major alias**，必须先查仓库 tag 列表。

---

### 坑 3：YAML 字符串含冒号必须加引号（静默杀手）

**症状**：workflow 触发后几秒 conclusion=failure，但 `gh run view <id> --json jobs` 显示 **jobs 数组为空**——一个 job 都没启动。

**根因**：GitHub Actions 在 yaml 解析失败时直接拒绝 workflow，不启动任何 job。最常见触发：
```yaml
CIBW_BEFORE_TEST: pip install --only-binary=:all: pyarrow  # 错!
```
`:all:` 第二个冒号被 YAML 解析为 mapping value delimiter，整个文件解析失败。

**修复**：整行加引号：
```yaml
CIBW_BEFORE_TEST: "pip install --only-binary=:all: pyarrow pandas"
```

**强制自检**（改完任何 workflow 后必跑）：
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
```
本地报错就修，不要 push 后等 GitHub 告诉你（GitHub 不给具体 yaml 错误行号，得自己查）。

**调试线索**：run conclusion=failure + jobs 为空 → 99% yaml 解析问题。

---

### 坑 4：CIBW_TEST_COMMAND 用 `{package}` 不要用 `{project}`

**症状**（monorepo + SDK 在子目录）：
```
ERROR: file or directory not found: /runner/work/<repo>/<repo>/tests
collected 0 items
============================ no tests ran in 0.00s =============================
```

**根因**：`{project}` 占位符替换为 cibuildwheel 调用的工作目录（**repo 根**），不是 `package-dir`。如果 SDK 在 `quant-sdk/` 子目录，测试在 `quant-sdk/tests/`，但 `{project}/tests` 会找 `<repo-root>/tests`，找不到。

**修复**：用 `{package}` 占位符：
```yaml
- uses: pypa/cibuildwheel@v3.4
  with:
    package-dir: quant-sdk
  env:
    CIBW_TEST_COMMAND: 'pytest {package}/tests -v -k "not requires_server"'
```

**占位符对照表**：

| 占位符 | 替换为 |
|---|---|
| `{project}` | cibuildwheel 调用的工作目录（repo 根） |
| `{package}` | `package-dir` 的绝对路径 |

**适用场景**：monorepo 必须用 `{package}`；单包仓库 `{project}` `{package}` 等价。习惯用 `{package}` 不会错。

---

### 坑 5：跨平台 shell 引号必须外单内双

**症状**（仅 Windows，linux/macos 正常）：
```
+ pytest D:\a\repo\repo\quant-sdk/tests -v -k 'not requires_server'
ERROR: file or directory not found: requires_server'
collecting ... collected 0 items
```

**根因**：Windows cmd **不解析单引号字符串**。`-k 'not requires_server'` 在 cmd 里被拆成两个独立参数 `'not` 和 `requires_server'`，pytest 把第二个当成目录路径。

**修复**：YAML value 外层用**单引号**，里面 shell 命令用**双引号**（双引号在 sh + cmd 都正常）：
```yaml
CIBW_TEST_COMMAND: 'pytest {package}/tests -v -k "not requires_server"'
```

**反例**（外双内单 = Windows 必坏）：
```yaml
CIBW_TEST_COMMAND: "pytest {package}/tests -v -k 'not requires_server'"  # 错!
```

**通用原则**：跨平台跑的命令字符串里，shell 引号统一用双引号；YAML 引号统一用单引号。**永远不要在跨平台命令里用单引号包参数**。

---

### 坑 6：manylinux 镜像必须升到 `_2_28`

**症状**（仅 linux 容器内 pip install 阶段）：
```
ERROR: Could not find a version that satisfies the requirement pyarrow (from versions: none)
ERROR: No matching distribution found for pyarrow
```

**根因**：`pyarrow` / `pandas` / `numpy` 等大型 C 扩展库**早已只发 `manylinux_2_28` wheel**（要求 glibc 2.28+，CentOS 8+ / Ubuntu 18.04+ / Debian 10+），**不再支持 `manylinux2014`**（glibc 2.17）。cibuildwheel 老配置默认起 `manylinux2014` 容器，容器内 pip 找不到任何匹配 wheel。

**修复**：
```yaml
env:
  CIBW_MANYLINUX_X86_64_IMAGE: manylinux_2_28
  CIBW_MANYLINUX_AARCH64_IMAGE: manylinux_2_28
  # musllinux 通常不用动
  CIBW_MUSLLINUX_X86_64_IMAGE: musllinux_1_2
  CIBW_MUSLLINUX_AARCH64_IMAGE: musllinux_1_2
```

**风险评估**：升 manylinux_2_28 提高了用户机器的 glibc 要求，但你的 SDK 既然依赖 pyarrow，用户本来就受这个约束，**所以不增加额外限制**。

**判断标准**：你的运行时依赖里有 pyarrow / pandas / numpy / scipy / lxml 等 → 必须 `manylinux_2_28`。

---

### 坑 7：测试阶段三方依赖必须强制 binary

**症状**（任意平台、最容易在 aarch64 触发）：
```
ERROR: Failed building wheel for libcst
error: can't find Rust compiler
ERROR: Failed to build 'pyarrow' when installing build dependencies for pyarrow
```

**根因**：cibuildwheel 在 test 阶段 `pip install <built-wheel>` 时自动装 SDK 的 runtime deps。pip 默认 prefer binary 但**允许源码 fallback**——某些版本/架构组合下 pip 找不到合适 binary，回退源码 build pyarrow → pyarrow build dep 拉 libcst → libcst 需要 Rust → 容器内没装 → 整个链 fail。

**修复**：在 test 前预装大依赖，**强制只用 binary**：
```yaml
env:
  CIBW_TEST_REQUIRES: pytest pytest-asyncio respx
  CIBW_BEFORE_TEST: "pip install --only-binary=:all: pyarrow pandas"
  CIBW_TEST_COMMAND: 'pytest {package}/tests -v -k "not requires_server"'
```

`--only-binary=:all:` 表示对**所有包**拒绝任何源码 build。找不到合适 wheel 直接 fail（快速明确），不会拉长得离谱的 build chain。

**关键**：必须搭配坑 6 的 `manylinux_2_28`，否则 pip 找不到 binary 直接报"No matching distribution"（参见坑 6 现象）。

---

### 坑 8：macos-13 runner 已退休（2025-12 起死等）

**症状**：workflow 长期卡在
```
Requested labels: macos-13
Waiting for a runner to pick up this job...
```
小时级 queued，runner 永远不分配。其他 job 都成功，publish 因 `needs: build_wheels` 一直不启动。

**根因**：GitHub 已于 **2025-12-04** 正式退役 `macos-13` runner image。配 `runs-on: macos-13` 的 job 不是排队，是 **runner pool 已被删空**——永远等不到。GitHub 没有为这种 case 抛错，只让你 queued 着。

Apple 完全停 Intel + GitHub 计划 **2027 秋停所有 x86_64 macOS runner**，整个 Intel Mac runner 时代在落幕。

**修复**：根据是否需要 macOS x86_64 wheel 选一：

```yaml
matrix:
  include:
    - { os: ubuntu-latest,    archs: x86_64 }
    - { os: ubuntu-24.04-arm, archs: aarch64 }
    # 选项 A: 仍需 x86_64 wheel(开发者自己是 Intel Mac / 重要用户群有 Intel Mac)
    - { os: macos-15-intel,   archs: x86_64 }   # ✅ 替代死掉的 macos-13(真 Intel runner)
    # 选项 B: 不需要 x86_64,删掉上一行,Intel Mac 用户走 Rosetta 跑 arm64 wheel
    - { os: macos-14,         archs: arm64 }
    - { os: windows-latest,   archs: AMD64 }
```

**其他可选替代 label**:

| label | 说明 |
|---|---|
| `macos-15-intel` | 真 Intel Mac runner(新引入,推荐) |
| `macos-14-large` / `macos-15-large` | Apple Silicon 上虚拟化跑 x86_64,贵且慢 |

**通用教训**：GitHub runner image 会按计划退役(macos-11/12/13 已退,macos-14 在用,macos-15 是新主力)。改 workflow 前去 https://github.com/actions/runner-images 看当前 supported labels;不要假设 stackoverflow 上的老 yaml 还能跑。

**自检**: 看 `Waiting for a runner` 卡超过 30 分钟,基本 100% 是 label 已死(而不是真排队)。

---

## 完整 workflow 模板

直接复制 `references/release-workflow-template.yml` 到项目 `.github/workflows/release.yml`，只改两处：

1. `package-dir: <PACKAGE_DIR>` → 实际 SDK 子目录（monorepo 必填）
2. `CIBW_BUILD` 行的 Python 版本枚举（按需调整）

模板已内置全部 7 项修复，开箱即用。

---

## Pre-flight checklist（发版前必跑）

```bash
# 1. 工作树干净
git status

# 2. tag 必须 = pyproject 版本（避开 workflow version_check 失败）
grep '^version = ' <PACKAGE_DIR>/pyproject.toml
git tag -l 'v*'

# 3. PyPI 上无该版本（PyPI 版本号永久不可重用！）
curl -s https://pypi.org/pypi/<your-package>/json \
  | python3 -c "import sys,json; print(list(json.load(sys.stdin).get('releases',{}).keys()))"

# 4. CHANGELOG 有新版本条目
head -20 <PACKAGE_DIR>/CHANGELOG.md

# 5. Trusted Publisher 已配（PyPI 网页 https://pypi.org/manage/account/publishing/ 确认）
#    owner = GitHub org，repo = GitHub repo 名（仓库改过名要同步改 PyPI！）
#    workflow = release.yml，environment = pypi

# 6. GitHub Environment "pypi" 存在
gh api repos/<owner>/<repo>/environments --jq '.environments[].name'

# 7. workflow yml 本地解析通过
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
```

---

## Build 失败后的安全重发流程

**前提**：PyPI 上还**没有 publish 成功**该版本号（PyPI 一旦 publish 成功，号码永久占用，必须 bump 下一个版本）。

```bash
# 1. cancel 失败 run，节省 CI 额度
gh run cancel <run-id>

# 2. 修代码 + commit + push
git add <修改文件>
git commit -m "ci(sdk): 修复 xxx"
git push origin main

# 3. 删本地 + 远端 tag，重打指向新 commit
git push origin :refs/tags/v0.4.0
git tag -d v0.4.0
git tag v0.4.0
git push origin v0.4.0

# 4. 监控新 run
run_id=$(gh run list --workflow=release.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch "$run_id" --exit-status
```

⚠️ **commit 前隔离 staging**：如果你边修边并行有其他文件改动，用 `git commit -- <specific-file>` 只 commit 指定文件，避免把不相关改动一起打包到"修复 commit"里污染历史。

---

## 调试技巧

| 场景 | 命令 |
|---|---|
| 看**进行中** job 的日志（`gh run view --log` 不让看 in-progress） | `gh api repos/<owner>/<repo>/actions/jobs/<job-id>/logs` |
| 拿失败 job ID 列表 | `gh run view <run-id> --json jobs --jq '.jobs[] \| select(.conclusion=="failure") \| "\(.databaseId) \| \(.name)"'` |
| 阻塞等待 run 完成（后台跑） | `gh run watch <run-id> --exit-status` |
| run 几秒 fail + jobs 为空 | 99% yaml 解析错误，本地跑 `python3 -c "import yaml; yaml.safe_load(...)"` |
| Filter 失败 job 关键错误 | `gh api .../jobs/<id>/logs \| grep -iE "error\|importerror\|cython\|setuptools\|packaging\|fatal\|not found"` |

---

## 仓库改名 / 迁移注意

GitHub repo 改名后：

- ✅ `Settings → Environments`（含 `pypi`）跟着 repo 保留，**不丢**
- ✅ Trusted Publisher 是绑 `owner/repo` 的，repo 改名后**必须**去 PyPI 改 publisher 配置（`https://pypi.org/manage/account/publishing/` → 找到 publisher → 改 repo 名），否则下次 publish 被 PyPI 拒绝
- ✅ 旧 repo URL 自动 301 redirect 一段时间，但建议立刻更新本地 `git remote set-url origin <新地址>`

---

## 不要做

- ❌ **不要在本地跑 `python -m build && twine upload`** —— 本地无法 build 跨平台 wheel，且容易绕过 Trusted Publisher 引入凭证管理风险
- ❌ **不要发 sdist 到 PyPI**（`pypa/gh-action-pypi-publish` 默认只发 wheel，保持这个行为）—— Cython 编译模块的 `.py` 源码会通过 sdist 完整泄漏，破坏混淆意义
- ❌ **不要假设 GitHub Action 的 `v<N>` major moving tag 一定存在**，先查仓库实际 tag 列表
- ❌ **workflow 改完不要直接 push**，先 `python3 -c "import yaml; yaml.safe_load(...)"` 本地验证
- ❌ **不要在 publish 前先发同版本号 sdist 占位** —— PyPI 同版本号占了就废，下次 publish 被拒
- ❌ **不要在 manylinux2014 容器里期望装上 pyarrow 24+ wheel** —— 必须 manylinux_2_28
- ❌ **跨平台命令里不要用单引号包参数** —— Windows cmd 不识别

---

## 违规检测清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| build-system 缺 packaging 锁 | 用 PEP 639 license 但 `[build-system].requires` 没列 `packaging>=24.2` | **致命 → 必坏** |
| YAML 含 `:` 未加引号 | env 值有 `=:all:` / `port:8080` 等冒号但整行未加引号 | **致命 → 必坏** |
| cibuildwheel 用 major alias | `pypa/cibuildwheel@v3`（不存在）/ `@v2`（不存在） | **致命 → 必坏** |
| TEST_COMMAND 用 `{project}` | monorepo 子目录 SDK 用 `{project}/tests` | 高 |
| TEST_COMMAND 外双内单 | `"... -k 'not xxx'"` Windows 必坏 | 高 |
| manylinux2014 + 大库依赖 | 依赖含 pyarrow/pandas/numpy 但 manylinux 镜像还是 2014 | 高 |
| 缺 CIBW_BEFORE_TEST binary 锁 | 大型 C 库依赖未预装 binary，源码 build 链失败 | 中 |
| 用了已退役 runner image | matrix 含 `macos-13` / `macos-12` / `macos-11` / `ubuntu-20.04` 等已下线 label | **致命 → 死等不报错** |
