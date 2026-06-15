---
name: dwy-github-action-publish
description: "GitHub Actions 打包分发避坑指南。先判断场景，再读取对应配置。场景 1：Python 含 C 扩展 / Cython / .so 的跨平台 wheel，用 cibuildwheel 构建并通过 PyPI Trusted Publisher(OIDC) 发布。场景 2：Electron 桌面应用多平台打包分发，用 electron-builder / electron-forge 在 macOS / Windows / Linux runner 上构建并发布 GitHub Release。覆盖 workflow YAML 解析、runner image 退役、matrix 拆分、跨平台 shell 引号、artifact/release、PyPI OIDC、Electron 签名/公证/Linux 依赖/产物命名等高频坑。触发条件：编辑或新建 .github/workflows/*.yml、用户说 GitHub Actions 打包 / 跨平台打包 / cibuildwheel / wheel build / Electron 打包 / electron-builder / electron-forge / GitHub Release 分发 / runner queued / workflow build 失败。"
---

# dwy-github-action-publish — GitHub Actions 打包分发避坑

定位：使用 GitHub Actions 做跨平台构建、打包、发布时，先判定产物类型，再查对应配置避坑。

本 skill 只处理 CI 打包分发链路。通用发版流程（测试 / bump / changelog / tag）走 `dwy-publish`；SDK 发布前安全审计走 `dwy-sdk-spec`；纯 Python 包不需要 cibuildwheel。

实战来源：

- Python wheel：quant-sdk 0.4.0 首发 PyPI 的 cibuildwheel 踩坑。
- Electron：某 Electron 桌面应用多平台打包（release.yml + build.yml + pack.mjs）实战配置。

---

## 先判断场景

先读用户目标和仓库配置，不要直接套模板。

| 场景 | 判断依据 | 必读配置 |
|---|---|---|
| Python wheel | `pyproject.toml` 含 `Cython` / `ext_modules` / `Extension` / 产物含 `.so` / 用户提 `cibuildwheel`、`wheel`、`PyPI` | `.github/workflows/*.yml`、`pyproject.toml`、`setup.py` / `setup.cfg`、`tests/` |
| Electron 桌面应用 | `package.json` 含 `electron` + `electron-builder` / `electron-forge`，用户提 Electron 多平台打包、GitHub Release、`dmg` / `exe` / `AppImage` | `.github/workflows/*.yml`、`package.json`、`electron-builder` 配置、`forge.config.*`、打包脚本 |

如果同时存在两个场景，拆成两个 workflow 或两个 job 组分别处理。不要把 Python wheel 的 PyPI OIDC 规则套到 Electron，也不要把 Electron 的签名/产物规则套到 Python wheel。

---

## 通用 GitHub Actions 检查

改任何 workflow 后先做这些检查。

```bash
# 1. YAML 必须能本地解析
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"

# 2. 检查 workflow 触发条件
gh workflow list
gh run list --workflow=release.yml --limit=5

# 3. run 几秒 fail 且 jobs 为空，多半是 YAML 解析失败
gh run view <run-id> --json jobs,conclusion
```

通用坑：

- GitHub Action 不一定有 `v<N>` major alias。改 `uses:` 前查对应仓库 tag。
- `run` / `env` 值里含 `:`、`=:all:`、`http://`、`${{ }}` 组合时，优先整体加引号。
- matrix 不要默认 `fail-fast: true`。跨平台打包应设 `fail-fast: false`，保留其他平台产物和日志。
- 不要使用退役 runner：`macos-13` / `macos-12` / `macos-11` / `ubuntu-20.04` 等会排队或失败。先查 `actions/runner-images` 当前 supported labels。
- 长时间卡 `Waiting for a runner to pick up this job...`，优先怀疑 runner label 已退役或额度/架构不可用。
- 发布 GitHub Release 需要 `permissions: contents: write`。
- PyPI Trusted Publisher 需要 `permissions: id-token: write`，并绑定 workflow 和 environment。
- artifact 名称必须包含平台和架构，避免多个 matrix 上传时互相覆盖。

---

## 场景 1：Python Cython wheel + PyPI OIDC

适用：含 Cython 编译扩展的 Python 包、跨平台 wheel 分发（linux x86_64/aarch64 + macOS x86_64/arm64 + Windows AMD64）、GitHub Actions + cibuildwheel + PyPI Trusted Publisher OIDC 发版。

模板：复制 `./references/release-workflow-template.yml` 到目标项目 `.github/workflows/release.yml`，只改：

1. `package-dir: <PACKAGE_DIR>`：实际 SDK 子目录；单包仓库填 `.` 或省略。
2. `CIBW_BUILD`：按需调整 Python 版本枚举。

### Python 必查配置

```bash
rg -n "Cython|ext_modules|Extension|cibuildwheel|pypa/gh-action-pypi-publish|license|version" pyproject.toml setup.py setup.cfg .github/workflows
```

检查点：

- `[build-system].requires` 含 `setuptools>=77`、`packaging>=24.2`、`wheel`、`Cython>=3.0.10`。
- `pypa/cibuildwheel` 用 minor tag 或精确 tag，例如 `pypa/cibuildwheel@v3.4`，不要写 `@v3`。
- monorepo 用 `with.package-dir`，测试命令使用 `{package}`，不要用 `{project}/tests`。
- 跨平台 shell 参数用外单内双：`'pytest {package}/tests -v -k "not requires_server"'`。
- Linux 依赖 pyarrow / pandas / numpy / scipy / lxml 时，manylinux 镜像用 `manylinux_2_28`。
- test 阶段大依赖用 binary-only 预装：`CIBW_BEFORE_TEST: "pip install --only-binary=:all: pyarrow pandas"`。
- macOS x86_64 用 `macos-15-intel`，不要用 `macos-13`。
- 默认只发布 wheel。不要发布 sdist，避免 Cython 编译模块源码随 sdist 泄漏。

### Python 8 个高频坑

#### 坑 1：PEP 639 license expression 触发 build env 依赖冲突

症状：

```text
ImportError: Cannot import `packaging.licenses`.
Setuptools>=77.0.0 requires "packaging>=24.2" to work properly.
```

根因：`pyproject.toml` 用 `license = "MIT"` 时，setuptools 77+ 校验 license expression 依赖 `packaging>=24.2`，cibuildwheel 临时 build env 可能装到旧 packaging。

修复：

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

#### 坑 2：cibuildwheel action 必须用 minor 级或精确 tag

症状：

```text
Unable to resolve action `pypa/cibuildwheel@v3`, unable to find version `v3`
```

修复：

```yaml
- uses: pypa/cibuildwheel@v3.4
# 或
- uses: pypa/cibuildwheel@v3.4.1
```

#### 坑 3：YAML 字符串含冒号必须加引号

错误：

```yaml
CIBW_BEFORE_TEST: pip install --only-binary=:all: pyarrow
```

正确：

```yaml
CIBW_BEFORE_TEST: "pip install --only-binary=:all: pyarrow pandas"
```

#### 坑 4：CIBW_TEST_COMMAND 用 `{package}` 不要用 `{project}`

```yaml
- uses: pypa/cibuildwheel@v3.4
  with:
    package-dir: quant-sdk
  env:
    CIBW_TEST_COMMAND: 'pytest {package}/tests -v -k "not requires_server"'
```

#### 坑 5：跨平台 shell 引号必须外单内双

错误：

```yaml
CIBW_TEST_COMMAND: "pytest {package}/tests -v -k 'not requires_server'"
```

正确：

```yaml
CIBW_TEST_COMMAND: 'pytest {package}/tests -v -k "not requires_server"'
```

#### 坑 6：manylinux 镜像必须升到 `_2_28`

```yaml
env:
  CIBW_MANYLINUX_X86_64_IMAGE: manylinux_2_28
  CIBW_MANYLINUX_AARCH64_IMAGE: manylinux_2_28
```

#### 坑 7：测试阶段三方依赖必须强制 binary

```yaml
env:
  CIBW_TEST_REQUIRES: pytest pytest-asyncio respx
  CIBW_BEFORE_TEST: "pip install --only-binary=:all: pyarrow pandas"
  CIBW_TEST_COMMAND: 'pytest {package}/tests -v -k "not requires_server"'
```

#### 坑 8：macos-13 runner 已退休

```yaml
matrix:
  include:
    - { os: ubuntu-latest,    archs: x86_64 }
    - { os: ubuntu-24.04-arm, archs: aarch64 }
    - { os: macos-15-intel,   archs: x86_64 }
    - { os: macos-14,         archs: arm64 }
    - { os: windows-latest,   archs: AMD64 }
```

---

## 场景 2：Electron 多平台打包 + GitHub Release

适用：Electron 桌面应用需要在 GitHub Actions 产出 macOS / Windows / Linux 安装包，并上传到 GitHub Release。

参考配置：

- `./references/electron-release-workflow-template.yml`

### Electron 必查配置

```bash
rg -n "electron|electron-builder|electron-forge|pack|dist|dmg|AppImage|nsis|appx|CSC|notar|publish|artifactName|extraResources|asar|submodules" package.json .github/workflows script src -g '!node_modules'
```

检查点：

- `package.json` 明确 `electron` 和打包工具版本，例如 `electron-builder`。
- workflow 用 `actions/checkout@v4`，项目依赖 submodule 时必须 `submodules: true`。
- Node 版本固定，例如 `actions/setup-node@v4` + `node-version: 20`。
- 使用锁文件安装：npm 项目用 `npm ci`，pnpm 项目用 `pnpm install --frozen-lockfile`。
- 每个平台在对应 runner 上打包，不要指望一个 Linux runner 交叉产出 macOS / Windows 完整安装包。
- macOS x64 和 arm64 分开：x64 用 `macos-15-intel`，arm64 用 `macos-latest` / `macos-14`。
- Linux AppImage 需要系统依赖，常见为 `icnsutils graphicsmagick xz-utils`。
- Linux runner 上 `apt-get update` 前可移除易失效的 Microsoft / Azure apt source，避免第三方源拖死打包。
- 未配置证书但要产出 unsigned 包时，设置 `CSC_IDENTITY_AUTO_DISCOVERY: false`，避免 electron-builder 自动找证书导致 macOS job 失败。
- 产物命名必须包含 `${version}`、`${os}`、`${arch}`，避免 Release asset 覆盖。
- upload-artifact 只上传最终安装包：`*.dmg`、`*.exe`、`*.AppImage`；不要上传 `win-unpacked/`。
- GitHub Release job 需要 `permissions: contents: write`，用 `actions/download-artifact@v4` + `merge-multiple: true` 汇总产物。

### Electron 推荐 workflow 形态

模板：复制 `./references/electron-release-workflow-template.yml` 到目标项目 `.github/workflows/release.yml`，再按项目实际包管理器、打包脚本、签名策略调整。完整 workflow 见该模板，下方高频坑解释各关键配置的原因。

### Electron 多平台高频坑

#### 坑 1：macOS x64 / arm64 不能混跑

macOS x64 用 `macos-15-intel`。macOS arm64 用 `macos-latest` / `macos-14`。不要用已退役的 `macos-13`。

#### 坑 2：Linux 打 AppImage 缺系统依赖

症状通常是图标转换、压缩、AppImage 生成失败。

```yaml
sudo apt-get install --no-install-recommends -y icnsutils graphicsmagick xz-utils
```

#### 坑 3：Ubuntu 第三方 apt 源拖死 `apt-get update`

GitHub hosted runner 预置源会变化。第三方源异常时，先移除无关 source。

```yaml
sudo rm -f /etc/apt/sources.list.d/azure-cli.list /etc/apt/sources.list.d/microsoft-prod.list
sudo apt-get update
```

#### 坑 4：未签名构建被 electron-builder 自动证书探测拖死

公开 unsigned 包或暂未配置证书时：

```yaml
env:
  CSC_IDENTITY_AUTO_DISCOVERY: false
```

如果需要签名/公证，显式配置 secrets：`CSC_LINK`、`CSC_KEY_PASSWORD`、`APPLE_ID`、`APPLE_APP_SPECIFIC_PASSWORD`、`APPLE_TEAM_ID`。不要同时依赖自动探测。

#### 坑 5：产物名不含平台架构导致 Release 覆盖

electron-builder 配置应使用稳定命名：

```js
artifactName: '${productName}-${version}-${os}-${arch}.${ext}'
```

#### 坑 6：只上传最终安装包

推荐：

```yaml
path: |
  release/**/*.dmg
  release/**/*.exe
  release/**/*.AppImage
```

需要自动更新时再上传 `*-latest.yml`。不要上传 `win-unpacked/`。

#### 坑 7：外部二进制资源必须在打包前下载

如果应用依赖 ADB、scrcpy server、native helper、Java/Android 构建产物，必须在 `npm run pack` 前完成下载或构建，并确保路径进入 `extraResources` / `files`。

#### 坑 8：Release job 必须先汇总 artifact 再发布

```yaml
- uses: actions/download-artifact@v4
  with:
    path: artifacts
    merge-multiple: true
```

发布前用 `find artifacts -type f` 打印文件列表，确认平台产物齐全。

---

## 安全重发流程

### Python PyPI

前提：PyPI 上还没有 publish 成功该版本号。PyPI 版本号一旦发布成功，永久不可复用，必须 bump 下一个版本。

```bash
gh run cancel <run-id>
git add <修改文件>
git commit -m "ci(sdk): 修复 xxx"
git push origin main
git push origin :refs/tags/v0.4.0
git tag -d v0.4.0
git tag v0.4.0
git push origin v0.4.0
gh run watch "$(gh run list --workflow=release.yml --limit=1 --json databaseId --jq '.[0].databaseId')" --exit-status
```

### Electron GitHub Release

如果 GitHub Release 已创建但产物错误，优先删错 release / tag 后重打，或 bump 版本。不要在同 tag 上混入不同 commit 的产物。

```bash
gh release view v1.2.3
gh release delete v1.2.3 --cleanup-tag
git tag v1.2.3
git push origin v1.2.3
```

执行删除前必须确认用户允许，因为这会删除远端 release / tag。

---

## 不要做

- 不要在本地跑 `python -m build && twine upload` 替代跨平台 wheel 发布。
- 不要给 Cython 包发布 sdist，除非明确接受源码泄漏。
- 不要假设 GitHub Action 有 major moving tag。
- 不要跳过 workflow YAML 本地解析。
- 不要用退役 runner label。
- 不要让多个 matrix 上传同名 artifact。
- 不要在 Electron 未配置签名时依赖证书自动探测。
- 不要把 `win-unpacked/`、中间目录、缓存目录发进 Release。
- 不要在一个 runner 上硬交叉构建所有 Electron 平台。

---

## 违规检测清单

| 检查项 | 违规模式 | 严重程度 |
|---|---|---|
| YAML 解析 | env / run 含 `:` 未加引号，run 几秒 fail 且 jobs 为空 | 致命 |
| action tag | `pypa/cibuildwheel@v3` 等不存在 alias | 致命 |
| runner | `macos-13` / `macos-12` / `ubuntu-20.04` | 致命 |
| artifact | matrix 上传同名产物或未带平台架构 | 高 |
| Python build-system | PEP 639 license 但缺 `packaging>=24.2` | 致命 |
| Python test path | monorepo 子目录用 `{project}/tests` | 高 |
| Python shell 引号 | Windows 跨平台命令里用单引号包参数 | 高 |
| Python manylinux | 大型 C 库依赖仍用 manylinux2014 | 高 |
| Electron macOS | x64 / arm64 未拆 runner | 高 |
| Electron Linux | AppImage 缺 `icnsutils graphicsmagick xz-utils` | 高 |
| Electron 签名 | unsigned 构建未设 `CSC_IDENTITY_AUTO_DISCOVERY: false` | 中 |
| Electron Release | 上传 unpacked 中间目录或漏最终安装包 | 高 |
