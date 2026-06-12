---
topic: partitioning
source_files:
  - official/db_distr_comp/db/db_partitioning.md
  - official/db_distr_comp/db/db_architecture.md
  - official/db_distr_comp/db/tsdb.md
  - official/db_distr_comp/db_oper/queries.md
  - official/funcs/a/addRangePartitions.md
  - official/funcs/a/addValuePartitions.md
  - official/funcs/d/dropPartition.md
  - official/funcs/c/createPartitionedTable.md
generated_at: 2026-05-19
---

# 分区策略与剪枝

## 何时用此主题

- "VALUE / HASH / RANGE / LIST / COMPO 该选哪个"
- "分区粒度多大合理 / 单分区多大"
- "为什么 SQL 没走分区剪枝 / 慢查询"
- "TSDB 的 sortColumns / sortKey 怎么设"
- "如何新增 / 删除分区"

## 5 种分区策略对比

DolphinDB 仅支持 5 种分区类型，由 `database()` 的 `partitionType` 指定。FLOAT/DOUBLE **不能**作为分区列。

| 策略 | 适用场景 | 自动扩展 | 单分区目标大小 | 注意点 |
|---|---|---|---|---|
| `VALUE` | 一个值一个分区，如交易日、月、设备 ID | `addValuePartitions` 追加 | 100MB – 1GB | 时间精度过高（TIME/SECOND/DATETIME）会产生百万级小分区，写入查询都会非常缓慢 |
| `HASH` | 已知分区数、分布列倾斜可控 | 不可扩展（数量建表时固定） | 100MB – 1GB | 不能保证大小一致；不适合连续范围查询；额外支持 LONG / UUID / IPADDR / INT128 |
| `RANGE` | 按区间，如 ID 段、价格段、字母段 | `addRangePartitions` 只能在尾部追加 | 100MB – 1GB | 区间含起始、不含结尾；新区间首元素必须等于原方案末元素 |
| `LIST` | 枚举多值聚成一个分区，如行业分组、几只股票一组 | 不可扩展 | 100MB – 1GB | 比 VALUE 灵活，可解决数据分布不均 |
| `COMPO`（组合） | 数据量极大、WHERE/GROUP BY 经常涉及多列 | 子层 RANGE/VALUE 可分别扩展（`level` 参数指层） | 100MB – 1GB | 仅支持 2 或 3 层；各层独立选 RANGE/VALUE/HASH/LIST；多列地位平等无优先级 |

粒度经验值（"控制分区粒度"章节）：单分区**未压缩** 100MB – 1GB，宽表可放宽；公式 S/8W（S=节点可用内存，W=worker 数）。降低粒度三招：用 COMPO、增分区数、RANGE 改 VALUE。

## sortColumns 规则（TSDB 专属）

`createPartitionedTable` 的 `sortColumns` 参数**只对 `engine="TSDB"` 数据库生效**。三个作用：确定索引键、数据排序、数据去重。

- **结构**：`sortColumns = [sortKey列..., 最后一列]`
  - 最后一列**必须**为时间类型或整型
  - 其余前 n-1 列组成 `sortKey`（索引键），不能为 TIME / TIMESTAMP / NANOTIME / NANOTIMESTAMP
  - 单列时该列即作为 sortKey，类型可放宽（同样禁用 TIME/TIMESTAMP/NANOTIME/NANOTIMESTAMP）
- **列数建议**：`sortColumns` ≤ 4 列；高频过滤字段优先靠前
- **基数建议**：每分区内 sortKey 组合数 **≤ 2000**；过多会让索引和读元数据开销反超收益
- **降维**：sortKey 组合数过多但每组合记录少时，用 `sortKeyMappingFunction` 降维；使用 `hashBucket` 时 buckets 不能与 HASH 分区数整除
- **去重 (`keepDuplicates`)**：`ALL`（默认）/ `LAST`（仅最新）/ `FIRST`（仅首条）；用 LAST 时支持 `softDelete`
- **常见误用**：把主键/唯一键塞进 `sortColumns`，导致单 sortKey 对应记录极少，TSDB 数据膨胀

## 分区剪枝判定（WHERE 写法）

来自 `db_oper/queries.md` "分区剪枝"章节，规则按分区类型区分：

**VALUE / RANGE / LIST 分区**：满足全部三条才剪枝
1. 过滤条件**仅含分区字段**、关系运算符（`<`, `<=`, `=`, `==`, `>`, `>=`, `in`, `between`）或逻辑运算符（`or`, `and`）、常量
2. **不能**包含链式条件（如 `100 < x < 200`）
3. 过滤逻辑能缩窄分区范围

**HASH 分区**：仅支持等值类运算符（`=`, `==`, `in`, `between`）+ `or` / `and` + 常量；分区字段为 STRING 时 **`between` 不剪枝**。

可剪枝写法：

```dolphindb
where date > 1990.12.01 - 10                            -- 常量运算合法
where date between 1990.08.01 : 1990.12.01              -- between 合法
where month(date) >= 1990.12M                           -- 低精度时间函数包裹合法（精度链 NANOTIMESTAMP > TIMESTAMP > DATETIME > DATEHOUR > DATE > MONTH > YEAR；TIME > SECOND > MINUTE > HOUR）
where date between 1990.08.01:1990.08.31 and y < 5      -- 系统先按 date 剪枝再用 y 过滤
```

不剪枝写法：

```dolphindb
where date + 30 > 2019.12.01            -- 分区字段被运算包裹
where 2019.12.01 < date < 2019.12.31    -- 链式比较
where y < 5                              -- 没有分区字段
where date < announcementDate - 3       -- 分区字段对比另一列而非常量
where y < 5 or date between ...         -- or 使过滤无法缩窄分区
```

`partitionFunc()` 分区列上的非等值比较（`>`, `<`）也不剪枝，见 `createPartitionedTable.md` "partitionColumns" 说明。

## 验证剪枝

```dolphindb
select [HINT_EXPLAIN] max(x) from pt where date between 1990.08.01:1990.12.01
```

`[HINT_EXPLAIN]` 打印执行计划，可观察实际扫描的分区数及执行顺序；详见 `progr/sql/hint.html`。TSDB 表在 WHERE 中进一步指定 sortKey 字段可进一步缩小到 block 级。

## 典型建表（COMPO + TSDB）

来自 `db_partitioning.md` "共存储"与"均匀分区"章节的真实写法：

```dolphindb
dateDomain = database("", VALUE, 2020.01.01..2030.01.01)            // 预留十年分区
buckets = cutPoints("A" + string(1..13) join string('B'..'Z'), 5)   // 防止字母分布不均
symDomain = database("", RANGE, buckets)
stockDB = database("dfs://stockDB", COMPO, [dateDomain, symDomain], engine="TSDB")

quoteSchema = table(10:0, `sym`date`time`bid`bidSize`ask`askSize,
                    [SYMBOL, DATE, TIME, DOUBLE, INT, DOUBLE, INT])
stockDB.createPartitionedTable(
    quoteSchema, `quotes, `date`sym,
    sortColumns = `sym`time,        // sortKey=sym（高频过滤靠前），最后一列 time
    keepDuplicates = `ALL,
    compressMethods = {time: "delta", bidSize: "delta", askSize: "delta"}
)
```

向 RANGE 层追加分区（`addRangePartitions` 用 `level` 指层）：

```dolphindb
addRangePartitions(db, 101 150 200 250, 1)   // 给 COMPO 第 1 层（ID）追加 3 个范围
db = database("dfs://compoDB")               // 完成后必须重新加载数据库
```

删除分区（`dropPartition`）：

```dolphindb
dropPartition(dbHandle=database("dfs://compoDB"), partitionPaths="/20170807/0_50", tableName=`pt)
dropPartition(dbHandle=database("dfs://compoDB"), partitionPaths=2017.08.08,        tableName=`pt, deleteSchema=true)
dropPartition(dbHandle=database("dfs://compoDB"), partitionPaths=[,[0,100]],        tableName=`pt)   // COMPO 二级，某层空数组占位
```

修改分布式表数据：先 `select` 出分区 → 内存修改 → `dropPartition` → `append!` 回写。

## 常见陷阱

- 用 FLOAT / DOUBLE 做分区列 → 报错 `The data type DOUBLE can't be used for a partition column`
- VALUE 分区用了 TIME / SECOND / DATETIME 这种高精度时间 → 百万级小分区
- STRING 直接当分区列 → 性能差，应先转 SYMBOL
- 分区字段写成 `where year(col)`、`where col + n > x`、`where 100 < col < 200` → 不剪枝
- 多 writer 选了"交易时刻"这种细碎字段做分区 → 事务冲突；应改成日期 / 股票代码
- sortKey 组合数 > 2000 / 把主键塞进 sortColumns → TSDB 膨胀，需 `sortKeyMappingFunction` 降维
- `addRangePartitions` 想在第一个分区前面加 → 不支持，只能尾部追加
- `dropPartition` 删 VALUE 一级分区后分区方案仍残留 → 需 `deleteSchema=true`（且数据库仅一张表）
- 不同分区机制的两张表 `join` → 不支持；要 join 必须同库 co-location（同分区方案、同分区列）

## 下钻原文

- `official/db_distr_comp/db/db_partitioning.md` — 5 种分区策略、粒度公式、cutPoints 均匀分区、co-location
- `official/db_distr_comp/db/tsdb.md` — sortColumns / sortKey / keepDuplicates 完整语义
- `official/db_distr_comp/db_oper/queries.md` — 分区剪枝判定规则、HINT_EXPLAIN
- `official/funcs/c/createPartitionedTable.md` — sortColumns、sortKeyMappingFunction、primaryKey、compressMethods 参数细节
- `official/funcs/a/addRangePartitions.md`、`official/funcs/a/addValuePartitions.md` — 追加分区
- `official/funcs/d/dropPartition.md` — 删除分区（路径模式 / 条件模式 / deleteSchema）
