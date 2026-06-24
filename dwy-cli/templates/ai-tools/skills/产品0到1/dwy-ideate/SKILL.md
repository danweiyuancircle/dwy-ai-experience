---
name: dwy-ideate
description: "【dwy·想法收敛】产品 0 到 1 立项第一步。触发场景：用户说『我有个想法 / 帮我把这个点子理清楚 / 想做个 XX / 收敛想法 / 立项 / ideate』，要把模糊念头通过苏格拉底式反问发散+收敛成清晰可执行的产品想法时。"
---

## 职责（单一）
把用户模糊的初始念头，通过苏格拉底式反问发散+收敛，产出一份清晰的产品想法定义。

## 输入（从哪读）
- 用户口述的初始想法（首个原子，无上游产出）

## 实现
[包装型] 对每个依赖的外部 skill（`brainstorming`）：
1. 先读本地缓存目录 `.dwy/prod/.cache/skills/<缓存目录名>/`
2. 命中（目录存在且含 SKILL.md）→ 读其 SKILL.md 执行，需要时一并用同目录 scripts/ 与配套 .md（如 brainstorming 的可视化服务器脚本）
3. 没命中 → 用 gh 拉**整个 skill 目录**到缓存：
   - 列文件：`gh api "repos/<repo>/git/trees/<tag>?recursive=1" --jq '.tree[]|select(.type=="blob")|.path' | grep "^<repo内目录>/"`
   - 逐文件拉并保原样（含脚本，base64 解码）：`gh api "repos/<repo>/contents/<path>?ref=<tag>" --jq '.content' | base64 -d` 写到 `.dwy/prod/.cache/skills/<缓存目录名>/<去掉 repo内目录前缀的相对路径>`，保持子目录结构（如 scripts/）
   - 更新 manifest.json（local 指向目录 `<缓存目录名>/`、记 repo + release_tag + fetched_at）
   - 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

依赖的外部 skill（缓存目录名 → repo / tag / repo内目录）：
- `brainstorming` → `obra/superpowers` / `v6.0.3` / `skills/brainstorming`

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/想法收敛.md`
- 固定章节：核心问题 / 目标用户 / 价值主张 / 关键假设 / 边界与不做什么
- 回写 state.json：`confirmed.idea`
