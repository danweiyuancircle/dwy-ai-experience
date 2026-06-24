---
name: dwy-competitor
description: "【dwy·竞品分析】产品 0 到 1 立项阶段。触发场景：用户说『分析竞品 / 看看市面上有啥 / 竞品调研 / 对标分析 / 市场上谁在做 / competitor』，想知道已有玩家、市场规模和差异化切入点时。"
---

## 职责（单一）
盘点已有竞品 + 估算市场规模，找出差异化切入点。

## 输入（从哪读）
- state.json 的 `confirmed.idea`
- `.dwy/prod/[项目]/01-立项/想法收敛.md`

## 实现
[包装型] 对每个依赖的外部 skill（`competitor-analysis`、`market-sizing`）：
1. 先读本地缓存目录 `.dwy/prod/.cache/skills/<缓存目录名>/`
2. 命中（目录存在且含 SKILL.md）→ 读其 SKILL.md 执行，需要时一并用同目录 scripts/ 与配套 .md（如 brainstorming 的可视化服务器脚本）
3. 没命中 → 用 gh 拉**整个 skill 目录**到缓存：
   - 列文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内目录>/"`
   - 逐文件拉并保原样（含脚本，base64 解码）：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d` 写到 `.dwy/prod/.cache/skills/<缓存目录名>/<去掉 repo内目录前缀的相对路径>`，保持子目录结构（如 scripts/）
   - 更新 manifest.json（local 指向目录 `<缓存目录名>/`、记 repo + release_tag + fetched_at）
   - 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

依赖的外部 skill（缓存目录名 → repo / tag / repo内目录）：
- `competitor-analysis` → `phuryn/pm-skills` / `v2.0.0` / `pm-market-research/skills/competitor-analysis`
- `market-sizing` → `phuryn/pm-skills` / `v2.0.0` / `pm-market-research/skills/market-sizing`

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/竞品分析.md`
- 固定章节：竞品清单 / 各竞品优劣 / 市场规模（TAM/SAM/SOM）/ 差异化切入点
- 回写 state.json：`confirmed.competitors`
