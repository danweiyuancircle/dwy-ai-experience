# 发版时按项目写 CHANGELOG

只在发版写。不发版不写、不升版本。

工厂是这次发版的 git 仓库根。工厂下可以有多个项目。每个项目可以各自有前端和后端。changelog 写在那一端自己的目录里。

## 先列出要写的端

1. 找出项目。一个项目是含有可独立发版的前端和/或后端的目录。常见是 `<项目>/frontend` 与 `<项目>/backend`。仓库根下直接就是这两端时，根就是这一个项目。目录名按仓库实际结构认，不套死 `frontend` / `backend` 这两个词。
2. 一端算存在：该目录有自己的版本来源（前端看 `package.json` 的 `version`，后端看 `pyproject.toml` 的 `version`），或有该端的应用入口。没有这一端就不写。
3. 决定哪些端要写：
   - 用户点名了项目或端：只写点名的。
   - 没点名：该端目录自上次 release tag 以来有提交才写。没有上次 tag 时，看这次准备发布的提交是否改过该目录。

```bash
git log <该端上次 tag>..HEAD --oneline -- <项目>/<端>/
```

4. 没有提交的端不写、不升版本、不打 tag。
5. 写之前先列出清单：项目、端、changelog 路径、有没有变更。清单里该写的还没写完，不进入 tag。

该项目下若还有 android / ios / harmony，同样各算一端，不写进前后端的 changelog。

## 落点

- `<项目>/frontend/CHANGELOG.md`
- `<项目>/backend/CHANGELOG.md`

只有一端的项目只写存在的那一端。不要在工厂根再写一份总表。

## 版本标题格式（与 git tag 对齐）

新版本必须用二级标题，版本串单独成标题，供打 tag 原样取用：

```markdown
# <包标识>          ← 作为 tag 的包前缀（如 shop-frontend、@acme/api）

## 0.16.1           ← 新版本标题；这一份 changelog 的 tag 版本串必须与此完全一致

### Patch Changes

- ...
```

约束：

- 标题里只写 SemVer 版本串，不要写 `v0.16.1`、日期或其它后缀
- 从 `develop` 发：标题是 `x.y.z-beta.N` 或 `x.y.z-rc.N`。从 `preview` 发正式版：标题是 `x.y.z`，不带预发布
- 该版本串 = 这一端版本来源文件里的 version = 这一份 changelog 即将打的 tag 中的版本部分（见 `git-tag.md`）
- 各端版本号各自维护。前端升了，不表示后端也要升

## 写法

1. 找这一端的上一个 release tag
2. 只取这一端目录里的 commit（命令见上）
3. 按 `feat` / `fix` / `refactor` / `chore` 分组
4. 写入这一端的 `CHANGELOG.md`，用 `## <新版本号>` 标注

仓库已有自动生成命令（changelogen 等）时优先使用。仍然只覆盖这一端的目录，版本标题仍要满足上面的格式。

写了几份 changelog，就按 `git-tag.md` 各打一个 tag。不要合成一个工厂级 tag。

## 自动执行

changelog 由 AI 生成并写入，不逐步确认。只有 commit 无法归类，或分不清项目边界时才问用户。

## 禁止

- 禁止在工厂根写一份总 CHANGELOG，把多个项目或前端后端混在一起
- 禁止只写了其中一个项目就进入 tag
- 禁止把 A 项目的 commit 写进 B 项目
- 禁止把前端的 commit 写进后端，或反过来
- 禁止给没有变更的端写一份空版本
- 禁止 changelog 未写完就进入 tag / 部署
- 禁止版本标题与这一份即将打的 tag 版本串不一致
