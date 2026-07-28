# CHANGELOG 按平台子目录各写一份

monorepo 下一个仓库可能同时含 android / ios / harmony / frontend / backend 多平台。**每个平台维护自己的 CHANGELOG，不写全局单份**。发哪个平台，只写哪个平台那份。

## 各平台 CHANGELOG 位置

- `android/CHANGELOG.md`
- `ios/CHANGELOG.md`
- `harmony/CHANGELOG.md`
- `frontend/CHANGELOG.md`
- `backend/CHANGELOG.md`

子目录名按仓库实际结构定（先在第 0 步识别平台目录）。单包仓库可在根目录一份；monorepo 按包目录（如 `dwy-cli/CHANGELOG.md`、`frontend/eui/CHANGELOG.md`）。

## 版本标题格式（与 git tag 对齐）

新版本必须用二级标题，版本串单独成标题，供第 6 步打 tag 原样取用：

```markdown
# <包标识>          ← monorepo 建议有 H1，作为 tag 的包前缀（如 create-dwy、@dwydev/eui）

## 0.16.1           ← 新版本标题；tag 版本串必须与此完全一致

### Patch Changes

- ...
```

约束：

- 标题里只写 SemVer 版本串（可含预发布，如 `1.0.0-rc.1`），不要写 `v0.16.1`、日期或其它后缀
- 该版本串 = 版本来源文件里的 version = 即将打的 tag 中的版本部分（见 `git-tag.md`）

## 写法

1. 找该平台上一个 release tag
2. 按平台子目录过滤 commit：

```bash
git log <last-tag>..HEAD --oneline -- <平台子目录>/
```

3. 按 `feat` / `fix` / `refactor` / `chore` 分组
4. 写入该平台 `CHANGELOG.md`，用 `## <新版本号>` 标注（格式见上）

如果仓库已有自动生成命令（changelogen 等），优先使用，但仍按平台目录过滤范围，且产出的版本标题须满足上述格式。

## 自动执行

changelog 由 AI 自动生成并写入，不强制逐步确认。仅当 commit 历史无法清晰归类、或平台目录边界不明时才停下问用户。

## 禁止

- 禁止写一份全局 CHANGELOG 混入多平台变更
- 禁止 changelog 未写完就进入 tag / 部署
- 禁止把其他平台的 commit 写进当前平台 CHANGELOG（必须按目录过滤）
- 禁止版本标题写成与即将打的 tag 版本串不一致的形式
