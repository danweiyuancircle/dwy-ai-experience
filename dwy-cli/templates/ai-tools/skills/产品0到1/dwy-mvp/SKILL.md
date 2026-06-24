---
name: dwy-mvp
description: "【dwy·MVP定义】产品 0 到 1 立项阶段（闸3）。触发场景：用户说『定义 MVP / 最小可行产品 / 先做哪些功能 / 砍功能 / 第一版做什么 / mvp』，要从想法收敛出第一版必须做的核心功能清单时。MVP 功能硬上限 ≤7 个。"
---

## 职责（单一）
从想法+验证结果，收敛出第一版 MVP 功能清单。**功能硬上限 ≤7 个**，超出的进后续版本。

## 输入（从哪读）
- state.json 的 `confirmed.idea`、`confirmed.validation`、`confirmed.poc`
- `.dwy/prod/[项目]/01-立项/想法收敛.md`、`需求市场验证.md`、`技术验证.md`

## 实现
[包装型] 对每个依赖的外部 skill（`prioritize-features`、`opportunity-solution-tree`）：
1. 先读本地缓存目录 `.dwy/prod/.cache/skills/<缓存目录名>/`
2. 命中（目录存在且含 SKILL.md）→ 读其 SKILL.md 执行，需要时一并用同目录 scripts/ 与配套 .md（如 brainstorming 的可视化服务器脚本）
3. 没命中 → 用 gh 拉**整个 skill 目录**到缓存：
   - 列文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内目录>/"`
   - 逐文件拉并保原样（含脚本，base64 解码）：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d` 写到 `.dwy/prod/.cache/skills/<缓存目录名>/<去掉 repo内目录前缀的相对路径>`，保持子目录结构（如 scripts/）
   - 更新 manifest.json（local 指向目录 `<缓存目录名>/`、记 repo + release_tag + fetched_at）
   - 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

依赖的外部 skill（缓存目录名 → repo / tag / repo内目录）：
- `prioritize-features` → `phuryn/pm-skills` / `v2.0.0` / `pm-product-discovery/skills/prioritize-features`
- `opportunity-solution-tree` → `phuryn/pm-skills` / `v2.0.0` / `pm-product-discovery/skills/opportunity-solution-tree`

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/MVP清单.md`
- 固定章节：MVP 功能清单（≤7 个）/ 优先级排序 / 砍到后续版本的功能
- **功能数超 7 个直接拒绝，强制收敛**
- 回写 state.json：`confirmed.mvp_features`
