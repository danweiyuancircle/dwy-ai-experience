# 发版 git tag（强制）

**每次更新版本号都必须打 tag 并推远端。** 无版本 bump 的纯重发 / 仅重跑 workflow / 仅回滚，不打新 tag。

## 时机

在第 3 步版本同步 + 第 4 步 changelog 写完、第 5 步安全检查通过之后：

1. 将版本来源文件 + CHANGELOG 一并 commit（若尚未提交）
2. 按下方规则算出 tag 名
3. 本地打 tag → push tag 到 origin
4. 再进入 build / 发布（若 workflow 由 tag 触发，push tag 即触发发布）

```bash
# 版本与 changelog 已落盘并 commit 后
git tag <tag>
git push origin <tag>
```

## tag 与 changelog 版本对齐（硬规则）

tag 中的**版本串**必须与本次 CHANGELOG **新版本标题**完全一致，禁止改写。

| CHANGELOG 写法 | 取出的版本串 |
|----------------|-------------|
| `## 0.16.1` | `0.16.1` |
| `## 2.2.3` | `2.2.3` |
| `## 1.0.0-rc.1` | `1.0.0-rc.1` |

禁止：

- changelog 写 `## 0.16.1`，tag 打成 `v0.16.1` / `0.16.1.0` / `0.16`（格式不一致）
- tag 版本与 `package.json` / `pyproject.toml` 等来源文件不一致
- 未写 changelog 新版本标题就打 tag

## tag 全名拼法

先取 changelog 版本串 `VER`，再按仓库惯例拼全名：

| 场景 | 规则 | 例 |
|------|------|-----|
| monorepo 多包 / 多平台 | `{包标识}@{VER}`；包标识优先取该 CHANGELOG 顶部 H1（去掉 `# `），否则取 `package.json` 的 `name` | CHANGELOG H1 `# create-dwy` + `## 0.16.1` → `create-dwy@0.16.1`；H1 `# @dwydev/eui` + `## 2.2.3` → `@dwydev/eui@2.2.3` |
| 单包仓库且历史 tag 已有固定前缀 | 沿用历史前缀 + `VER`（仅当前缀不篡改 VER 本身时） | 历史 `v1.2.0` 且 changelog 为 `## 1.3.0` 时，若项目约定 `v` 前缀且 VER 仍完整出现 → 须在本仓库已有 tag 惯例中确认；**优先保证 VER 与 changelog 一致** |
| 单包仓库无历史惯例 | 直接用 `VER` | changelog `## 1.0.0` → tag `1.0.0` |

**冲突裁决**：若「历史 `v` 前缀」与「changelog 无 `v`」冲突，以 **changelog 标题里的版本串** 为准拼 tag（monorepo 用 `包@VER`，单包用 `VER`），不要为了凑 `v` 前缀改掉 VER。仓库若已有 workflow 写死 `v*` 触发，同步改 workflow 或 changelog 标题约定，二者必须一致。

打 tag 前自检：

```bash
# VER 必须等于 changelog 最新 ## 标题
# 包来源文件 version 字段必须等于 VER
git tag -l | head   # 对照历史命名是否 monorepo 包前缀
```

## 推送与触发

- 必须 `git push origin <tag>`，只打本地 tag 不算完成
- method 为 `github-action` / `github-action-oidc` 且 workflow `on.push.tags` 时：push tag 即触发 CI，不必再另起发布命令
- method 为 local / testflight / maven 等：先 push tag，再跑缓存的 `publish_cmd`（或按项目既有顺序，但 tag 不可省）

## 重发 / 删 tag

远端已有错误 tag 需要覆盖时：

1. **先确认用户允许**删除远端 tag / release
2. 再删远端 + 本地，重打同名 tag 推送

```bash
git push origin :refs/tags/<tag>
git tag -d <tag>
git tag <tag>
git push origin <tag>
```

## 禁止

- 禁止版本号已 bump 却不打 tag
- 禁止 tag 版本串与 changelog 新版本标题不一致
- 禁止 tag 与版本来源文件不一致
- 禁止未 push 远端就当发版完成
- 禁止未确认用户就删除远端已有 tag / release
