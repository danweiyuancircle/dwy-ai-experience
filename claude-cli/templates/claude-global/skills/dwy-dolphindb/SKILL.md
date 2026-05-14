---
name: dwy-dolphindb
description: >
  DolphinDB 开发规范与最佳实践审查。当用户要求生成、修改、审查或优化涉及
  DolphinDB 的 Python/SQL 代码、脚本拼接、批量写入、查询优化、连接管理、分区
  裁剪、分区方案设计（OLAP/TSDB/PKEY 引擎单分区大小估算、范围/值/哈希分区选型）、
  STRING/BLOB/SYMBOL 字段长度限制、数据类型转换、Docker 配置或测试 Mock 时，
  **必须**使用此 skill。即使用户没有明确提到 "DolphinDB"，但只要代码中出现
  dolphindb、run_ddb、loadTable、append!、dropPartition、DBConnectionPool、
  DDBSession、tickDB、factorDB、addRangePartitions、newValuePartitionPolicy
  等关键字，或涉及 TSDB 分区、时间序列数据库存储、金融 tick 数据/因子数据写入，
  也要触发此 skill。用于确保代码符合社区版 8GB 内存限制、2 节点集群限制、
  分区裁剪（包括禁止链式比较 `a <= col <= b`）、输入校验、批量写入 ≤500K 行、
  SYMBOL ≤255 字节、单分区大小落在引擎推荐区间等硬约束。
---

# DolphinDB 开发规范 Skill

## 何时使用

只要任务涉及以下任一内容，立即读取 `references/dolphindb-rules.md` 并按本 skill 执行审查：

- 编写或修改调用 DolphinDB 的 Python 代码（`run_ddb`、`run_ddb_with_data`、`DDBSession`、`DBConnectionPool` 等）
- 编写或修改 DolphinDB 脚本（`loadTable`、`append!`、`dropPartition`、`select` 等）
- 批量写入 tick 数据或因子数据到 DolphinDB
- 查询 DolphinDB 中的 tick/因子数据，尤其是 WHERE 条件设计
- 数据类型转换（Feather/Pandas → DolphinDB）
- Docker 中部署或配置 DolphinDB
- 为 DolphinDB 相关代码编写测试 Mock
- 代码审查（CR）时发现文件包含 DolphinDB 调用

## 使用步骤

### 1. 加载完整规则

读取 `references/dolphindb-rules.md`。该文件包含全部 12 章规则，是审查的唯一权威来源。

### 2. 识别代码中涉及的规则章节

根据当前任务内容，判断主要涉及哪些章节：

| 任务类型 | 重点章节 |
|---|---|
| 查询脚本编写 | 三（分区裁剪）、八（查询优化） |
| 建库建表/分区方案设计 | 十二（分区设计原则） |
| 批量数据写入 | 二（连接管理）、四（批量写入）、十（数据类型映射）、十三（字符串长度限制） |
| 脚本拼接/动态生成 | 五（脚本语法）、六（输入校验） |
| 服务层 Python 代码 | 二（连接管理）、六（输入校验）、十（数据类型映射） |
| Docker/部署配置 | 九（Docker 环境） |
| 测试代码 | 十一（测试 Mock） |
| 代码审查/CR | 全部，尤其是十四（检查清单） |

### 3. 执行规则审查

对生成的或已有的代码，逐条检查相关章节的**强制规则**和**违规检测**项。

**审查输出格式：**

对每处问题，使用以下格式报告：

```
⚠️ [规则章节] 具体问题
   违规代码：<摘录>
   修复建议：<具体修改后的代码>
   原因：<引用规则中的说明>
```

对符合规则的代码，可以简要确认：

```
✅ [规则章节] 符合要求 — <简要说明>
```

### 4. 特别关注以下致命违规

以下问题会直接导致生产故障或 OOM，必须零容忍：

1. **分区列被函数包裹**（如 `date(trade_date)`）→ 全表扫描 → 8GB OOM
2. **链式比较过滤**（如 `2022.12.01 <= TradeDate <= 2022.12.03`）→ 不触发分区剪枝 → 全表扫描
3. **单次 append 超过 500K 行** → TSDB 报错 `exceeds max limit`
4. **未校验的外部输入拼接到脚本** → 脚本注入风险
5. **连接池做 upload + run** → 变量跨连接不可见
6. **select *** → 传输全部 30+ 列，浪费带宽和内存
7. **分页使用 `LIMIT x OFFSET y`** → DolphinDB 不支持 OFFSET 关键字
8. **`asyncio.to_thread(pool.run, script)`** → SDK v3 的 `pool.run()` 已是原生 async，无需包装
9. **SYMBOL 列写入未校验长度** → 超 255 字节抛异常，整批写入失败
10. **建表分区方案过细**（如每天 5000+ 个 0.6MB 小分区）→ 命中 `maxPartitionNumPerQuery=65536` 限制

### 5. 检查清单应用

如果任务是**代码审查**或**最终确认**，逐条过一遍 `references/dolphindb-rules.md` 第十四章的检查清单（13 项），并给出通过/不通过的明确结论。

## 输出要求

- 审查结果必须结构化，按规则章节分组
- 对每一处违规，必须给出**可落地的修复代码**，不能只说"不符合规则"
- 如果代码完全符合规则，明确声明"所有 DolphinDB 相关规则检查通过"
- 如果任务只是生成代码，在生成过程中就内联应用规则，生成完毕后给出简要的合规确认
