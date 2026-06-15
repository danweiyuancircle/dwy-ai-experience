---
name: dwy-code-flow-docs
description: 代码逻辑梳理文档。把指定的代码流程整理成非 IT 人员能看懂的 Markdown 文档(Mermaid 流程图 + 概述 + 关键配置 + 依赖关系)。触发场景:用户说"梳理 XX 逻辑"/"整理 XX 流程"/"帮我梳理一下 XXX"(创建)、"更新 XX 逻辑"/"刷新 XX 文档"(更新)、"现在梳理了哪些逻辑"/"列出已梳理的流程"(查询)、"强制重新梳理 XX"/"重扫 XX"(重扫)。文档存在用户指定根目录,扁平结构+中文文件名,YAML frontmatter 记录 sources + git commit,更新时先用 git diff 判断有无变化,无变化跳过、有变化只读 diff,大幅节省 token。
---

# dwy-code-flow-docs

把代码流程梳理成非 IT 人员能看懂的 Markdown 文档。Claude 主动读代码,套统一模板,放在用户指定根目录。

---

## 何时触发

| 用户原话样例 | 操作类型 |
|---|---|
| 梳理 XX 逻辑 / 整理 XX 流程 / 帮我梳理一下 XXX | **创建** |
| 更新 XX 逻辑 / 刷新 XX 文档 / 重新梳理 XX(无"强制") | **更新** |
| 现在梳理了哪些逻辑 / 列出已梳理的流程 / 已经梳理过哪些 | **查询** |
| 强制重新梳理 XX / 重扫 XX / rescan XX | **重扫** |

---

## 根目录配置

每个项目第一次使用时,先确认存储根目录。

### 读取顺序
1. 读项目根 `.claude/code-flow-docs.config`,格式 `root=<绝对路径>`
2. 文件不存在 → 问用户:"代码逻辑文档存到哪里?给我一个绝对路径"
3. 拿到路径后:
   - 检查路径父目录存在;不存在则提示用户先创建
   - 写入 `.claude/code-flow-docs.config`,内容仅一行 `root=<绝对路径>`
   - 在该路径下创建 `INDEX.md`(若不存在)

### 配置文件示例
```
root=/Users/chances/WebstormProjects/ai-quant/docs/code-flows
```

---

## 操作:创建新文档

1. 从用户原话提取**逻辑名称**(如"配额计算"、"因子流式查询")
2. 目标路径 = `<root>/<逻辑名称>.md`
3. 文件已存在 → 提示"该逻辑已梳理过,是否要更新?",改走**更新**流程
4. 文件不存在 → 进入读代码阶段:
   - 用 Grep 工具按关键词扫描(中英混合,如 `quota|配额|billing|deduct`)
   - 读相关文件,弄清楚流程
   - 按 `templates/logic-doc.md` 套模板生成文档
   - 写质量参照 `examples/配额计算.md`
5. **写 YAML frontmatter(必填,不可省略)**:
   - `title`: 逻辑名称
   - `updated`: 今天日期 (YYYY-MM-DD)
   - `last_commit`: `git rev-parse HEAD` 的完整 hash
   - `sources`: 实际读过的文件**相对项目根**的路径列表
   - `scan_keywords`: 这次 grep 用过的关键词列表
6. 更新 INDEX.md(不存在则按 `templates/INDEX.md` 创建),新增一行
7. 输出文件**完整绝对路径**给用户

---

## 操作:更新已有文档

**核心:先 git diff 判断有无变化,无变化直接退出,不读代码。**

1. 读 `<root>/<逻辑名称>.md` 的 YAML frontmatter,拿 `last_commit` 和 `sources`
2. 跑命令(**不带 HEAD,含未提交改动**):
   ```bash
   git diff --stat <last_commit> -- <sources 列表展开>
   ```
3. 输出为空 → 告诉用户:
   > "自 `<last_commit 短 hash>` 以来,相关代码无变化。文档已是最新,无需更新。"
   退出,不做任何写入。
4. 有输出 → 跑 `git diff <last_commit> -- <sources>` 看具体 diff hunk
5. 只读 diff 涉及的代码片段(不读完整文件,除非 diff 涉及的函数依赖外部上下文)
6. 重写整个文档(整篇重写策略),更新 frontmatter:
   - `updated`: 今天日期
   - `last_commit`: 当前 `git rev-parse HEAD` 的完整 hash
   - `sources`: 如果有新增相关文件,加入列表
7. 更新 INDEX.md 对应行的"更新时间"
8. 输出:"已更新 `<完整绝对路径>`,本次变化:`<git diff --stat 摘要>`"

---

## 操作:查询梳理过的逻辑

1. 读 `<root>/INDEX.md`
2. 直接把表格输出给用户

INDEX.md 不存在 → "还没梳理过任何逻辑,说'梳理 XX 逻辑'开始第一个。"

---

## 操作:强制重扫

用户说"强制重新梳理 XX" / "重扫 XX" / "rescan XX":

1. 读现有文档的 `scan_keywords`
2. 用这些关键词重新 grep,允许找到新文件(扩大 sources)
3. 走"创建新文档"完整流程,覆盖原文件
4. 更新 `sources`(可能扩大)和 `last_commit` 和 `updated`
5. 更新 INDEX.md 对应行

---

## 写作规范(产出文档质量底线)

### 通用
- 面向**非 IT 读者**。避免行话(如 channel、pub-sub、middleware、callback)。必须用专业词时,后面括号补一句白话解释。
- 时间统一 `YYYY-MM-DD`,不要 `2026/5/17` 或 `5月17日`。

### 1. 概述 (1 段, 3-5 句)
讲清楚"这段代码是做什么的、解决什么问题、什么时候被触发"。

### 2. 实现逻辑

#### 流程图 (Mermaid `flowchart`,**只用 flowchart,禁止 sequenceDiagram**)
- 节点用中文标签
- 决策点用 `{}` 菱形
- 主路径 + 异常路径都画
- 节点数 5-15 个;超 15 个考虑拆子流程

#### 关键步骤 (3-7 条有序列表)
每条:**步骤名**: 一句话解释**做什么** + 一句话解释**为什么这么做**

### 3. 关键配置 (表格)
- 列:`配置项 | 默认值 | 说明 | 位置`
- 位置格式 `` `相对路径:行号` ``
- **只列有人会改的配置**(超时、TTL、批大小、开关、阈值、Cron 表达式),硬编码常量不列

### 4. 依赖关系 (bullet)
- 每个依赖:**名称**: 用途 + 涉及的 key/表/接口
- **最后一行必须明确写"不依赖什么"**(常见组件:PostgreSQL/Redis/DolphinDB/MinIO/外部 API),避免读者猜测

---

## 文件结构

### Skill 端
```
.claude/skills/dwy-code-flow-docs/
├── SKILL.md                  ← 本文件
├── templates/
│   ├── logic-doc.md          ← 单文档模板
│   └── INDEX.md              ← 总目录模板
└── examples/
    └── 配额计算.md            ← 质量样本(参考它的详尽程度)
```

### 产出端(用户指定的 root)
```
<root>/
├── INDEX.md
├── 配额计算.md
├── 因子流式查询.md
└── 用户鉴权.md
```

---

## 禁止

- 禁止把代码原文大段贴进文档(读者是非 IT 人员)
- 禁止用 ASCII 流程图(必须用 Mermaid)
- 禁止时序图 `sequenceDiagram`(只用 `flowchart`)
- 禁止时间格式不一致
- 禁止省略 frontmatter(下次更新就丢失增量优化能力)
- 禁止不更新 INDEX.md(总目录必须和实际文件同步)
- 禁止跳过 git diff 直接重读所有代码(违反 token 优化原则)
