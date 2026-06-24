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
- 拉新：按新 tag 重新 WebFetch 对应 SKILL.md，覆盖本地缓存文件 + 更新 manifest

### 职责②：可选一键全量预热
- 把全部外部 skill 一次拉到本地（本质 = 对所有外部各跑一遍懒加载）
- 适合首次进项目、或离线前预热

### 职责③：维护 manifest.json
- 每次拉取后写回 `fetched_at` / `release_tag` / `local`

## 当前 stable 版本
- pm-skills：`v2.0.0`（repo `phuryn/pm-skills`）
- superpowers：`v6.0.3`（repo `obra/superpowers`）

## 缓存结构
`.dwy/prod/.cache/skills/`：
- `manifest.json` — 索引
- `pm__<name>.md` — pm-skills 来源
- `sp__<name>.md` — superpowers 来源

## manifest.json 格式
```json
{
  "version": "1.0",
  "skills": {
    "pm/competitor-analysis": {
      "repo": "phuryn/pm-skills",
      "release_tag": "v2.0.0",
      "fetched_at": "2026-06-24T00:00:00Z",
      "local": "pm__competitor-analysis.md"
    }
  }
}
```
