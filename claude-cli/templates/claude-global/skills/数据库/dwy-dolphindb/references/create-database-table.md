# 建库建表

## 30 秒选型

| 你的数据 | 引擎 | 分区策略 | 排序列 |
|---|---|---|---|
| 行情快照 / tick / 逐笔 / level2 | **TSDB** | `VALUE(日期), HASH(SymbolField, N)` | `[SecurityID, TradeTime]` |
| 分钟/日 K 线 / 因子结果 | **OLAP** | `VALUE(日期)` 或 `RANGE(月份)` | — |
| 维度信息（股票基础信息表等） | — | 维度表（不分区） | — |
| 流式行情写入 + 实时查询 | TSDB | 同 tick | 同 tick |

**OLAP vs TSDB**：
- OLAP = 列存，写入快，**不支持点查/更新**。适合 K 线、因子、批分析。
- TSDB = 列存 + 索引，**支持 sortKey 排序+索引**，秒级点查。适合 tick/snapshot/逐笔，分区 400MB-1GB。
- 选错了改不了，整个库 drop 重建。

## 分区策略

| 类型 | 关键字 | 自动扩展 | 适用 |
|---|---|---|---|
| VALUE | `VALUE(2024.01.01..2024.12.31)` | ✅ | 日期、状态 |
| HASH | `HASH([SYMBOL, 50])` | ✅ | 高基数列（股票代码） |
| RANGE | `RANGE(0 100 200 300)` | ❌ 需 `addRangePartitions` | 数值范围 |
| LIST | `LIST([['A','B'], ['C']])` | ❌ | 明确分组 |
| COMPO | `partitioned by VALUE(...), HASH(...)` | 看子分区 | 复合（最多 3 级）|

**分区层级硬限制**：1-3 级。常用 2 级 = `日期 + 股票代码 HASH`。

**分区粒度目标**：单分区压缩后 **TSDB 400MB-1GB / OLAP 100MB-300MB**。粒度太细 → 元数据爆炸；太粗 → 查询不能并行。

**`maxPartitionNumPerQuery` 硬限**：默认 65536。单次查询触达的分区数超过这个值直接报 `The number of partitions relevant to the query is too large`。

### 分区设计反例（**新手最常踩**）

> 股票行情数据（每天 5000 万条），先按 `TradeDate` 值分区，再按 `SecurityID` 二级 VALUE 分区。
> A 股 5000+ 标的 → **一天 5000 个分区，每个仅 0.6MB**。

后果：
- 查 14 天 → 70000 分区 → 超 65536 上限报错
- 单分区 0.6MB 远低于 TSDB 400MB 下限，元数据开销 > 数据本身
- 列存收益丧失，查询比单级分区还慢

**修复**：二级改 `HASH([SYMBOL, 50])`（固定 50 桶），每天 50 个分区，单分区 60MB（仍偏小但元数据 OK）。

### VALUE 分区自动扩展

```dolphindb
// 库参数：写入新值时自动建分区
create database "dfs://xxx"
    partitioned by VALUE(2024.01.01..2024.01.07)
    engine='TSDB',
    newValuePartitionPolicy=add        // 关键：新日期自动建分区，不需预创建
```

不设 `newValuePartitionPolicy=add` → 写入未预建的日期会报 `partition does not exist`。

### RANGE 分区静默丢弃陷阱

```dolphindb
// 库参数 allowMissingPartitions 默认 true
// → 范围外数据【静默丢弃，不报错】！
create database "dfs://xxx"
    partitioned by RANGE(2024.01M..2024.12M)
    // 写 2025 年数据 → 默默丢

// 需要严格性：
create database "dfs://xxx"
    partitioned by RANGE(2024.01M..2024.12M),
    allowMissingPartitions=false       // 越界写入直接报错
```

RANGE 分区**不会**自动扩展，必须手动 `addRangePartitions(database, futureRanges)`。

### 估算 HASH 桶数

```
桶数 ≈ (每日数据量 / 期望单分区大小)
```

A 股 5000+ 股票 + level2 一天 ~80GB → 按日期分区后 80GB / 1GB ≈ 80 桶 → 取 `HASH([SYMBOL, 50])`（保守留 buffer）。

## 建库 DDL

### 行情快照（TSDB + COMPO 分区）

```dolphindb
// 删库重来（开发期）
if(existsDatabase("dfs://stock_lv2_snapshot")) {
    dropDatabase("dfs://stock_lv2_snapshot")
}

create database "dfs://stock_lv2_snapshot"
    partitioned by VALUE(2024.01.03..2024.01.04), HASH([SYMBOL, 50]),
    engine='TSDB'
    // VALUE 写头 2 天即可，写入新日期会自动扩展；写多了只是元数据占位
```

**注意**：
- `VALUE` 用一小段日期初始化即可，会自动扩展，**不要塞几年的空分区**（元数据膨胀）。
- 删库用 `dropDatabase`，要在 controller 上跑。
- `engine='TSDB'` 不写默认是 OLAP。

### 分钟 K 线（OLAP + 单级 VALUE）

```dolphindb
if(existsDatabase("dfs://k_minute_level")) {
    dropDatabase("dfs://k_minute_level")
}

create database "dfs://k_minute_level"
    partitioned by VALUE(2024.01.01..2024.01.31)
    engine='OLAP'
```

### 维度表（不分区，跟在某个 DFS 库下）

```dolphindb
db = database("dfs://stock_lv2_snapshot")
createDimensionTable(db, "security_info",
    table(1:0, ["SecurityID","Name","Industry"], [SYMBOL,STRING,SYMBOL])
)
```

## 建表 DDL

### TSDB 表（必须 sortColumns）

```dolphindb
create table "dfs://stock_lv2_snapshot"."snapshot"(
    TradeDate DATE[comment="交易日期", compress="delta"]
    TradeTime TIME[comment="交易时间", compress="delta"]
    SecurityID SYMBOL
    LastPrice DOUBLE
    OpenPrice DOUBLE
    HighPrice DOUBLE
    LowPrice DOUBLE
    TotalVolumeTrade LONG
    OfferPrice DOUBLE[]          // 数组向量：10 档卖价
    BidPrice DOUBLE[]
    OfferOrderQty LONG[]
    BidOrderQty LONG[]
)
partitioned by TradeDate, SecurityID,
sortColumns=["SecurityID","TradeTime"],
keepDuplicates=ALL
```

**关键参数**：
- `partitioned by`：必须和库的 partition 顺序一致。
- `sortColumns`：**最后一列必须是时间列**，前面是高频查询的过滤列（如 `SecurityID`）。
- `keepDuplicates`：`ALL`（保留）/`FIRST`/`LAST`，金融 tick 一般 `ALL`。
- `compress="delta"`：单调递增列（日期、时间、序号）必加，能压缩 80%+。
- `DOUBLE[]`：数组向量类型，10 档行情用一列搞定（vs 拆 20 列）。

### OLAP 表（轻量，无 sortColumns）

```dolphindb
create table "dfs://k_minute_level"."k_minute"(
    securityid SYMBOL
    tradetime TIMESTAMP
    open DOUBLE
    close DOUBLE
    high DOUBLE
    low DOUBLE
    vol INT
    val DOUBLE
    vwap DOUBLE
)
partitioned by tradetime
```

## sortColumns 选择规则（TSDB）

✅ 推荐：`[业务键, 时间列]` —— `[SecurityID, TradeTime]`、`[InstrumentID, Timestamp]`

❌ 禁止：
- 把**唯一键/主键**当 sortColumn（如订单号、UUID）→ 索引膨胀，TSDB 索引文件比数据还大
- **时间列放第一位** → 同一时刻的不同标的散开，按 SecurityID 查变慢

## 数据类型选择

| 场景 | 类型 | 不要用 |
|---|---|---|
| 价格、金额（金融） | `DECIMAL32(3)` / `DECIMAL64(6)` | `FLOAT/DOUBLE`（精度丢失） |
| 成交量、笔数 | `LONG`（大数）/ `INT`（小数） | — |
| 股票代码、合约代码 | `SYMBOL` | `STRING`（symbol 列式压缩 + 字典编码更省） |
| 名称、备注 | `STRING` | — |
| 日期 | `DATE` | — |
| 时间戳 | `TIMESTAMP`（毫秒）/`NANOTIMESTAMP`（纳秒） | `DATETIME`（32 位 int，2038 溢出！）|
| 10 档行情 | `DOUBLE[]` 数组向量 | 拆 20 列（写慢、查慢） |

## ALTER 限制（建表前想清楚）

| 操作 | TSDB | OLAP |
|---|---|---|
| 新增列（只能末尾） | ✅ | ✅ |
| 删列 | ❌ | ✅（非分区列） |
| 改列名 | ❌ | ✅（非分区列） |
| 改列类型 | ❌ | ✅（非分区列） |
| 改列顺序 | ❌ | ❌ |
| 改分区列 | ❌ | ❌ |
| 主键/唯一索引 | ❌ | ❌ |
| 自增列 | ❌ | ❌ |

**结论**：TSDB 表 schema 一旦定下基本不能动。建表前用一周数据 dry-run。

## 元数据查询

```dolphindb
getClusterDFSDatabases()                       // 所有 DFS 库
getClusterDFSTables("dfs://stock_lv2_snapshot")// 库下所有表
getTables(database("dfs://xxx"))               // 同上
schema(loadTable("dfs://xxx","t"))             // 完整 schema
getDatabaseDDL("dfs://xxx")                    // 反查建库 SQL
getDBTableDDL("dfs://xxx","t")                 // 反查建表 SQL
getTableDiskUsage("dfs://xxx","t")             // 表占用磁盘
```

跨引用：导入数据 → [[data-import]]，查询 → [[crud-operations]]，反模式 → [[pitfalls-and-best-practices]]。
