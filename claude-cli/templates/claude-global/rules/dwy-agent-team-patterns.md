---
description: Agent 并行模式速查表(任务级/步骤级并行场景与 worktree 指南)
---

# Agent 并行模式速查表

常见任务的 Agent 并行分工模板。执行前对照此表选择合适的模式。

## 一、任务级并行模式

### 模式 1：批量创建（N 路并行）

**场景：** 创建多个独立的组件/页面/测试/demo

```
示例："给 5 个组件写 demo 页面"

Agent-1 (worktree) → ComponentA demo
Agent-2 (worktree) → ComponentB demo
Agent-3 (worktree) → ComponentC demo
Agent-4 (worktree) → ComponentD demo
Agent-5 (worktree) → ComponentE demo
→ 全部完成后 code-reviewer 审查
```

**要点：**
- 每个 Agent 使用 `isolation: "worktree"`
- 每个 Agent 的 prompt 包含组件的 API 说明和 demo 规范
- 风险等级：低，直接执行

### 模式 2：研究 + 实现（2 阶段流水线）

**场景：** 需要先了解代码再动手修改

```
示例："修复 EForm 组件的验证 bug"

阶段 1（并行研究）：
  Agent-Explore → 分析 EForm 组件代码结构和数据流
  Agent-Explore → 搜索相关测试和使用示例
  Agent-Explore → 查看 git 历史和相关 issue

阶段 2（串行实现）：
  基于研究结果，主线程或单 Agent 实现修复

阶段 3（并行验证）：
  Agent → 运行测试
  Agent → code-review 变更
```

**要点：**
- 阶段 1 的 Agent 全部用 `subagent_type: "Explore"`
- 阶段 2 必须等阶段 1 全部完成
- 风险等级：中，阶段 2 前需确认方案

### 模式 3：多模块同步修改

**场景：** 一个功能涉及多个独立模块的修改

```
示例："给所有 API 模块添加分页参数"

Agent-1 (worktree) → 修改 user API 模块
Agent-2 (worktree) → 修改 order API 模块
Agent-3 (worktree) → 修改 product API 模块
→ code-reviewer 审查一致性
```

**要点：**
- 每个 Agent 必须收到统一的修改规范（参数命名、类型定义）
- 使用 worktree 隔离
- 风险等级：中，执行前确认修改规范

### 模式 4：前后端同步开发

**场景：** 接口契约已定，前后端可以同时写

```
示例："新增用户导出功能"

Agent-1 (worktree) → 后端 API + service 实现
Agent-2 (worktree) → 前端页面 + API 调用
→ code-reviewer 审查接口契约一致性
```

**要点：**
- 两个 Agent 必须收到相同的接口契约定义（URL、参数、响应格式）
- 风险等级：中，确认接口契约后执行

## 二、步骤级并行模式

### 模式 A：并行信息收集

在执行任何任务前，将独立的信息收集步骤并行化：

```
同一消息中发起：
  Grep → 搜索相关代码引用
  Glob → 查找相关文件
  Read → 读取配置文件
  Agent(Explore) → 分析依赖关系
```

### 模式 B：并行验证

修改完成后，将独立的验证步骤并行化：

```
同一消息中发起：
  Bash → 运行单元测试
  Bash → 运行 lint 检查
  Bash → 运行类型检查
  Bash → 运行构建
```

### 模式 C：并行文档/测试补充

主要代码完成后，并行补充配套文件：

```
同一消息中发起：
  Agent → 写单元测试
  Agent → 更新相关文档
  Agent → 更新 changelog
```

## 三、反模式（禁止使用）

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 多 Agent 改同一文件 | 冲突、覆盖 | 串行修改或拆分文件职责 |
| 无上下文的 Agent | 产出质量差 | prompt 必须自包含 |
| 链式依赖硬并行 | B 依赖 A 的输出却并行 | 识别依赖，串行执行 |
| 超过 5 个 Agent 同时派出 | 难以管理、context 爆炸 | 单批最多 5 个 Agent |
| 跳过 review 直接提交 | 质量无保障 | 遵循 review 闭环 |

## 四、Agent 数量指南

| 场景 | 建议 Agent 数 |
|------|-------------|
| 批量创建同质文件 | 每个文件 1 个，上限 5 个/批 |
| 并行研究 | 2-3 个 Explore Agent |
| 多模块修改 | 每个模块 1 个，上限 4 个/批 |
| 前后端同步 | 2 个 |
| 步骤级并行工具调用 | 不限（Grep/Glob/Read 等轻量调用尽量并行） |

超过 5 个 Agent 的任务，分批执行：先派第一批，完成后再派第二批。

## 五、Worktree 使用指南

以下场景**必须**使用 `isolation: "worktree"`：

- 多个 Agent 各自创建/修改不同文件
- Agent 的修改可能与当前工作区冲突
- 需要保持主工作区干净（如正在进行其他工作）

以下场景**不需要** worktree：

- 纯只读的 Explore Agent
- 步骤级并行的工具调用（Grep/Glob/Read/Bash）
- 单个 Agent 执行（无冲突风险）
