---
name: dwy-version
description: "【dwy·版本规划】产品 0 到 1 需求规划阶段。触发场景：用户说『版本规划 / 排版本 / 版本路线图 / V1 做啥 V2 做啥 / roadmap』，要把 PRD 需求按版本切片排路线图时。准出复查 V1.0 范围不膨胀。"
---

## 职责（单一）
把 PRD 需求按版本切片，排出版本路线图。准出复查 V1.0 范围没膨胀。

## 输入（从哪读）
- state.json 的 `confirmed.prd`、`confirmed.mvp_features`
- `.dwy/prod/[项目]/02-需求规划/PRD.md`

## 实现
[包装型] 对每个依赖的外部 skill（`outcome-roadmap`、`prioritize-features`）：
1. 先读本地缓存目录 `.dwy/prod/.cache/skills/<缓存目录名>/`
2. 命中（目录存在且含 SKILL.md）→ 读其 SKILL.md 执行，需要时一并用同目录 scripts/ 与配套 .md（如 brainstorming 的可视化服务器脚本）
3. 没命中 → 用 gh 拉**整个 skill 目录**到缓存：
   - 列文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内目录>/"`
   - 逐文件拉并保原样（含脚本，base64 解码）：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d` 写到 `.dwy/prod/.cache/skills/<缓存目录名>/<去掉 repo内目录前缀的相对路径>`，保持子目录结构（如 scripts/）
   - 更新 manifest.json（local 指向目录 `<缓存目录名>/`、记 repo + release_tag + fetched_at）
   - 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

依赖的外部 skill（缓存目录名 → repo / tag / repo内目录）：
- `outcome-roadmap` → `phuryn/pm-skills` / `v2.0.0` / `pm-execution/skills/outcome-roadmap`
- `prioritize-features` → `phuryn/pm-skills` / `v2.0.0` / `pm-product-discovery/skills/prioritize-features`

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/版本路线图.md`
- 固定章节：版本切片（V1.0/V1.x/V2.0…）/ 各版本目标 / V1.0 范围准出复查
- **V1.0 范围超出 MVP 清单直接告警，强制收敛**
- 回写 state.json：`confirmed.version_plan`
