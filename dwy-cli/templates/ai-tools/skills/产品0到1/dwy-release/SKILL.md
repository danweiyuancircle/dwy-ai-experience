---
name: dwy-release
description: "【dwy·上架迭代】产品 0 到 1 上架迭代阶段（终点）。触发场景：用户说『上架 / 发布上线 / 出上架物料 / 配埋点 / 规划下一版 / release』，要准备上架物料、埋点指标并规划下一版迭代时。"
---

## 职责（单一）
产出上架物料 + 埋点指标设计 + 下一版迭代规划。

## 输入（从哪读）
- state.json 的 `confirmed.acceptance`、`confirmed.prd`、`confirmed.version_plan`
- `.dwy/prod/[项目]/04-上线交付/验收报告.md`
- `.dwy/prod/[项目]/02-需求规划/版本路线图.md`

## 实现
[包装型] 对每个依赖的外部 skill（`release-notes`、`gtm-strategy`、`metrics-dashboard`、`north-star-metric`）：
1. 先读本地缓存目录 `.dwy/prod/.cache/skills/<缓存目录名>/`
2. 命中（目录存在且含 SKILL.md）→ 读其 SKILL.md 执行，需要时一并用同目录 scripts/ 与配套 .md（如 brainstorming 的可视化服务器脚本）
3. 没命中 → 用 gh 拉**整个 skill 目录**到缓存：
   - 列文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内目录>/"`
   - 逐文件拉并保原样（含脚本，base64 解码）：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d` 写到 `.dwy/prod/.cache/skills/<缓存目录名>/<去掉 repo内目录前缀的相对路径>`，保持子目录结构（如 scripts/）
   - 更新 manifest.json（local 指向目录 `<缓存目录名>/`、记 repo + release_tag + fetched_at）
   - 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

依赖的外部 skill（缓存目录名 → repo / tag / repo内目录）：
- `release-notes` → `phuryn/pm-skills` / `v2.0.0` / `pm-execution/skills/release-notes`
- `gtm-strategy` → `phuryn/pm-skills` / `v2.0.0` / `pm-go-to-market/skills/gtm-strategy`
- `metrics-dashboard` → `phuryn/pm-skills` / `v2.0.0` / `pm-product-discovery/skills/metrics-dashboard`
- `north-star-metric` → `phuryn/pm-skills` / `v2.0.0` / `pm-marketing-growth/skills/north-star-metric`

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/04-上线交付/上架物料.md`、`埋点与指标.md`、`下一版迭代规划.md`
- 固定章节：
  - 上架物料.md：发布说明 / GTM 策略 / 渠道文案
  - 埋点与指标.md：北极星指标 / 埋点清单 / 指标看板设计
  - 下一版迭代规划.md：数据反馈方向 / 下一版功能候选 / 优先级
- 回写 state.json：`confirmed.release`（上架物料就绪 + 下一版迭代方向）
