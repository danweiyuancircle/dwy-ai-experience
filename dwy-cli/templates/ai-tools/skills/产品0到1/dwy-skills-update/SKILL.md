---
name: dwy-skills-update
description: "【dwy·外部skill缓存管理】管理产品 0 到 1 流程依赖的外部 skill 本地缓存。触发场景：用户说『更新外部 skill / 检查 pm-skills 有没有新版 / 预热全部 skill 缓存 / 同步 superpowers / 维护 manifest / skills update』，要比对 GitHub 正式 release 拉新、或一次性预热全部外部 skill 时。"
---

## 职责
管理 `.dwy/prod/.cache/skills/` 下外部 skill（pm-skills、superpowers）的本地缓存。三项职责：

### 职责①：比对 stable release 更新
- 只认**正式 release**：跳过 prerelease / beta / rc / 含 `-` 的 tag
- 取最新 stable：`gh release list --repo <repo> --exclude-pre-releases` 或 GitHub API（`/releases/latest`），过滤 tag 含 `-` 的
- 与 `manifest.json` 记录的 `release_tag` 比对：**有更高版才拉新**，否则跳过
- 拉新：按新 tag 用 gh api 拉**整个 skill 目录**（不止 SKILL.md），覆盖本地缓存目录 + 更新 manifest

### 职责②：可选一键全量预热
- 把全部外部 skill **整目录**一次拉到本地（本质 = 对所有外部各跑一遍懒加载）
- 适合首次进项目、或离线前预热

### 职责③：维护 manifest.json
- 每次拉取后写回 `fetched_at` / `release_tag` / `local`

## 当前 stable 版本
- pm-skills：`v2.0.0`（repo `phuryn/pm-skills`）
- superpowers：`v6.0.3`（repo `obra/superpowers`）

## 缓存结构
`.dwy/prod/.cache/skills/`：
- `manifest.json` — 索引
- `<skill名>/` — 每个外部 skill 一个目录（无 sp/pm 前缀），含 `SKILL.md` + 配套 `scripts/` + 其他 `.md`，保持源仓库子目录结构

外部 skill 目录不止 SKILL.md：superpowers 的 `brainstorming` 带 `scripts/`、`systematic-debugging` 带 11 个文件，只缓存 SKILL.md 会丢配套。一律缓存整个目录。

## 拉取方式（整目录，gh api）
1. 列目录文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内skill目录>/"`
2. 逐文件拉内容并 base64 解码、保原样：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d > .dwy/prod/.cache/skills/<skill名>/<相对路径>`
3. 保持子目录结构（如 `scripts/`），落到 `.dwy/prod/.cache/skills/<skill名>/` 下

## manifest.json 格式
key 用 skill 名（无 `pm/` `sp/` 前缀），`local` 指向缓存目录：

```json
{
  "version": "1.0",
  "skills": {
    "competitor-analysis": {
      "repo": "phuryn/pm-skills",
      "release_tag": "v2.0.0",
      "fetched_at": "2026-06-24T00:00:00Z",
      "local": "competitor-analysis/"
    }
  }
}
```
