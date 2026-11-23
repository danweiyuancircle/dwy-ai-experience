# 项目级 schema / 慢查询 注入协议

> 何时引用：用户问"这个 SQL 为何慢"、"评估这个建表语句"、"分析这个查询的内存占用"等性能/审查问题。
> 协议目的：让 LLM 基于用户真实环境的 DDL 和 SQL 给出针对性建议，而不是泛泛而谈。

## 协议总览

用户在自己项目根目录手动维护两个文件夹（不进 git 模板仓库，避免泄露生产环境信息）：

```
{项目根}/.claude/dolphindb/
├── schemas/
│   ├── {库名}.{表名}.dos      ← 真实 CREATE TABLE / createPartitionedTable 语句
│   └── ...
└── slow_queries/
    ├── {名字}.sql              ← 待优化的 DDB SQL
    └── {名字}.note.md          ← 这条查询的现象描述（耗时 / 数据量 / 报错）
```

## LLM 行为约定（写到 SKILL.md 路由表）

当用户问"评估这个查询性能"或粘贴 SQL 让你分析时：

1. **先 `ls {项目根}/.claude/dolphindb/schemas/`**，看是否有相关表的 DDL
2. **有** → 读出 DDL，基于真实分区策略 / sortColumns / 数据类型 / 压缩配置给评估
3. **无** → 主动提示用户：

```
没找到这张表的 schema。要做准确的性能评估，需要你把这张表的真实建表语句粘到：

  {项目根}/.claude/dolphindb/schemas/{库名}.{表名}.dos

例如要分析 dfs://stock/quote 的 trade 表慢查询，建个文件：

  .claude/dolphindb/schemas/stock_quote.trade.dos

里面贴你在 DDB 上跑 schema(loadTable('dfs://stock/quote', 'trade')) 拿到的 DDL，
或者直接贴当初的 createPartitionedTable 调用脚本。

贴完再问我，我可以基于实际分区粒度 / sortColumns / 数据类型给建议。
```

## 慢查询接入

用户也可以把待评估的 SQL 长期沉淀下来，便于多轮迭代：

```
.claude/dolphindb/slow_queries/2024Q1_pivot.sql       ← 这条 SQL 原文
.claude/dolphindb/slow_queries/2024Q1_pivot.note.md   ← 配套说明：耗时 35s / 涉及表 / 内存占用 / 现象
```

`.note.md` 推荐字段（自由格式）：

```markdown
# 2024Q1_pivot

- 现象：本地集群跑 35 秒返回；昨天还是 8 秒
- 输入数据量：trade 表，2024-01-01 ~ 2024-03-31，约 1.2 亿行
- 报错（如有）：无
- 期望：< 5 秒
- 已尝试：加了 between 替代链式比较，没明显提升
- 涉及 schema：见 schemas/stock_quote.trade.dos
```

LLM 拿到完整三件套（DDL + SQL + note）后，结合 [[review-rules/anti-patterns]] 和 [[review-rules/perf-baselines]] 给具体修复建议。

## 隐私 / 安全

- `.claude/dolphindb/` 目录用户**应当** `.gitignore` 加进忽略列表（含真实表结构 / 真实 SQL，不建议提交）
- skill 仓库本身不带任何示例 DDL（避免被误以为是生产 schema）
- 用户自己粘贴的内容只在本地，dwy sync 也不会动这些文件
