---
name: dwy-tdd-dev
description: "【dwy·TDD开发】产品 0 到 1 开发阶段。触发场景：用户说『开始开发 / 写代码 / TDD 开发 / 按任务开发 / 实现功能 / tdd』，要按模块循环 RED→GREEN→REFACTOR 开发并自动推进时。单元测试归此阶段。"
---

## 职责（单一）
按模块循环 RED→GREEN→REFACTOR 开发，测试通过自动进下一模块（无人工逐模块验收）。单元测试归此阶段。

## 输入（从哪读）
- state.json 的 `confirmed.tasks`、`confirmed.architecture`、`confirmed.dev_progress`
- `.dwy/prod/[项目]/02-需求规划/开发任务拆解.md`
- `.dwy/prod/[项目]/03-设计与架构/技术架构.md`、`数据库设计.md`、`接口契约.md`

## 实现
[包装型] 对每个依赖的外部 skill（`test-driven-development`、`systematic-debugging`）：
1. 先读本地缓存目录 `.dwy/prod/.cache/skills/<缓存目录名>/`
2. 命中（目录存在且含 SKILL.md）→ 读其 SKILL.md 执行，需要时一并用同目录 scripts/ 与配套 .md（如 brainstorming 的可视化服务器脚本）
3. 没命中 → 用 gh 拉**整个 skill 目录**到缓存：
   - 列文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内目录>/"`
   - 逐文件拉并保原样（含脚本，base64 解码）：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d` 写到 `.dwy/prod/.cache/skills/<缓存目录名>/<去掉 repo内目录前缀的相对路径>`，保持子目录结构（如 scripts/）
   - 更新 manifest.json（local 指向目录 `<缓存目录名>/`、记 repo + release_tag + fetched_at）
   - 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

依赖的外部 skill（缓存目录名 → repo / tag / repo内目录）：
- `test-driven-development` → `obra/superpowers` / `v6.0.3` / `skills/test-driven-development`
- `systematic-debugging` → `obra/superpowers` / `v6.0.3` / `skills/systematic-debugging`

每模块循环：RED 写失败测试 → GREEN 最小实现通过 → REFACTOR 重构。测试通过自动进下一模块。

## 产出契约（硬约束）
- 落到：项目源码目录 + 各模块单元测试 + `.dwy/prod/[项目]/09-开发日志.md`
- 固定章节（开发日志）：模块进度 / 关键决策 / 遇到的问题与解法
- 回写 state.json：`confirmed.dev_progress.<module> = todo|done`（逐模块维护）
