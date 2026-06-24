---
name: dwy-prd
description: "【dwy·PRD生成】产品 0 到 1 需求规划阶段。触发场景：用户说『写 PRD / 出需求文档 / 产品需求文档 / prd』，要把 MVP 清单细化成可开发的产品需求文档时。"
---

## 职责（单一）
把 MVP 功能清单细化成完整可开发的 PRD。

## 输入（从哪读）
- state.json 的 `confirmed.mvp_features`、`confirmed.idea`
- `.dwy/prod/[项目]/01-立项/MVP清单.md`

## 实现
[包装型] 对每个依赖的外部 skill（`create-prd`）：
1. 先读本地缓存目录 `.dwy/prod/.cache/skills/<缓存目录名>/`
2. 命中（目录存在且含 SKILL.md）→ 读其 SKILL.md 执行，需要时一并用同目录 scripts/ 与配套 .md（如 brainstorming 的可视化服务器脚本）
3. 没命中 → 用 gh 拉**整个 skill 目录**到缓存：
   - 列文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内目录>/"`
   - 逐文件拉并保原样（含脚本，base64 解码）：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d` 写到 `.dwy/prod/.cache/skills/<缓存目录名>/<去掉 repo内目录前缀的相对路径>`，保持子目录结构（如 scripts/）
   - 更新 manifest.json（local 指向目录 `<缓存目录名>/`、记 repo + release_tag + fetched_at）
   - 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

依赖的外部 skill（缓存目录名 → repo / tag / repo内目录）：
- `create-prd` → `phuryn/pm-skills` / `v2.0.0` / `pm-execution/skills/create-prd`

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/PRD.md`
- 固定章节：背景与目标 / 用户场景 / 功能需求（逐条）/ 非功能需求 / 验收标准
- 回写 state.json：`confirmed.prd`
