---
topic: engines
source_files:
  - official/db_distr_comp/db/tsdb.md
  - official/db_distr_comp/db/olap.md
  - official/db_distr_comp/db/pkey_engine.md
  - official/db_distr_comp/db/imoltp.md
  - official/db_distr_comp/db/vectordb.md
generated_at: 2026-05-19
---

# DolphinDB 5 大存储引擎选型

## 何时用此主题

用户问"该用 TSDB 还是 OLAP"、"PKEY 能不能改主键"、"VECTORDB 性能如何"、"行情数据用什么引擎"、"主键 CDC 同步进 DolphinDB 怎么选" 等引擎选型问题时进来。

## 核心要点

- **OLAP / TSDB / PKEY / VECTORDB 都是 DFS 分布式引擎**，建库时通过 `engine='TSDB'|'OLAP'|'PKEY'` 指定；VECTORDB 是 TSDB 之上的索引能力，仍设 `engine="TSDB"`。
- **IMOLTP 是单节点纯内存引擎**，库路径必须以 `oltp://` 开头，须在配置文件设 `enableIMOLTPEngine=true`，且当前版本不支持分区。
- **TSDB 必填 `sortColumns`**（最后一列必须是 INTEGER 或 TEMPORAL 类型），可选 `keepDuplicates`（ALL/LAST/FIRST）；PKEY 必填 `primaryKey`，可选 `indexes`（仅支持 bloomfilter）。
- **TSDB 的去重策略影响更新代价**：`keepDuplicates=LAST` 走追加更新最高效；`ALL/FIRST` 要全分区读改写。
- **主键唯一性 + 实时更新只有 PKEY 能做**：TSDB LAST 能"查询不返回重复行"但磁盘有冗余且无非主键索引；OLAP 不支持去重。
- **TSDB 单分区推荐 400MB–1GB（压缩前），`sortColumns` 不超过 4 列，单分区 sortKey 组合数建议 < 2000**。

## 引擎横向对比

| 引擎 | 存储模式 | 主键/索引 | 更新支持 | 典型场景 | 关键配置 |
|---|---|---|---|---|---|
| OLAP | DFS 列存（顺序追加，单列单文件） | 无主键，无索引 | 支持 update/delete，但按分区全量读改写，代价大 | 全表/全分区批量扫描分析（如全市场交易量统计） | `OLAPCacheEngineSize`、`compressMethods` |
| TSDB | DFS 列存 + LSM-Tree + sortKey 索引 + zonemap | `sortColumns`（最后一列 INTEGER/TEMPORAL，前 n-1 列作 sortKey） | LAST 追加更新高效；ALL/FIRST 按分区重写 | 时序点查（行情/IoT/宽表/array vector/BLOB） | `sortColumns`、`keepDuplicates`、`sortKeyMappingFunction`、`TSDBCacheEngineSize` |
| PKEY | DFS 列存 + LSM-Tree + Merge-on-Write + delete bitmap | `primaryKey`（必含分区列），可加 `indexes={"col":"bloomfilter"}`（zonemap 自动建） | 近实时更新，主键唯一性保证 | OLTP CDC 同步入仓、Ad-Hoc 查询、需要主键唯一约束的场景 | `primaryKey`、`indexes`、`PKEYCacheEngineSize`、`PKEYDeleteBitmapUpdateThreshold` |
| IMOLTP | 单机内存行存 + B+ 树（OLC 算法） + WAL/Checkpoint | `primaryKey` 必填，可加多个 `secondaryKey`（unique/non-unique） | 完整 ACID 跨表事务（`transaction` 块、commit/rollback） | 高并发 OLTP（订单/交易系统），数据量受单机内存限制 | `enableIMOLTPEngine=true`、库前缀 `oltp://`、`createIMOLTPTable` |
| VECTORDB | TSDB 之上对 `FLOAT[]` 列建 Faiss 向量索引（每个 Level File 一份） | 继承 TSDB 的 `sortColumns`；额外 `indexes={"col":"vectorindex(type=..., dim=...)"}` | 同 TSDB，且 `keepDuplicates=ALL` 强制 | 向量相似度检索（RAG/推荐/图搜） | 索引类型 Flat/PQ/IVF/IVFPQ/HNSW；查询走 `rowEuclidean + ORDER BY ASC + LIMIT` |

## 选型决策树

```
1. 单机、数据量 <= 内存、需要完整 ACID 跨表事务？
   → IMOLTP
2. 需要向量相似度检索（RAG/嵌入/相似图）？
   → VECTORDB（TSDB engine + vectorindex）
3. 需要主键唯一性 + 实时更新 + 非主键列索引（OLTP CDC 入仓）？
   → PKEY
4. 时序数据点查 / 宽表 / array vector / 频繁按 sortKey 过滤？
   → TSDB
5. 仅做大批量顺序写 + 全分区扫描分析，不需要去重和点查？
   → OLAP
```

## 典型用法

TSDB 建库建表（行情场景，按日期 VALUE + 股票 HASH 组合分区）：

```dolphindb
db1 = database(, VALUE, 2024.01.01..2024.12.31)
db2 = database(, HASH, [SYMBOL, 50])
db  = database(directory="dfs://stock_tsdb", partitionType=COMPO,
               partitionScheme=[db1, db2], engine="TSDB")

tb = table(1:0, `SecurityID`TradeDate`TradeTime`Price`Volume,
                [SYMBOL, DATE, TIME, DOUBLE, INT])

db.createPartitionedTable(table=tb, tableName=`trade,
    partitionColumns=`TradeDate`SecurityID,
    sortColumns=`SecurityID`TradeTime,
    keepDuplicates=LAST)
```

OLAP 建库建表（仅做批量扫描分析，无去重需求）：

```dolphindb
db = database(directory="dfs://stock_olap", partitionType=VALUE,
              partitionScheme=2024.01.01..2024.12.31, engine="OLAP")

tb = table(1:0, `SecurityID`TradeDate`Price`Volume,
                [SYMBOL, DATE, DOUBLE, INT])

db.createPartitionedTable(table=tb, tableName=`trade,
                          partitionColumns=`TradeDate)
```

## 常见陷阱

- **TSDB sortKey 当主键用导致库膨胀**：把唯一约束设为 `sortColumns`，每个 sortKey 只对应几行，元数据膨胀，极端场景数据库放大 50 倍。需主键唯一性请改用 PKEY。
- **TSDB `keepDuplicates=ALL/FIRST` 的更新踩坑**：每次更新按分区全量读取到内存改写，分区过大可能 OOM；高频更新场景必须用 `LAST`。
- **TSDB 整分区扫描不如 OLAP**：TSDB 增加了索引和 Cache Engine 排序开销，整列扫描场景 OLAP 更快。
- **PKEY 写入吞吐量上限低于 TSDB**：吞吐量增长后 PKEY 写入耗时上升更快，纯高吞吐写入用 TSDB。
- **VECTORDB Cache Engine 中数据无索引**：刚写入的向量在 Cache Engine 中只能穷举搜索，需 `flushTSDBCache()` 强制落盘后才走向量索引。
- **VECTORDB 查询限制多**：必须 `ORDER BY rowEuclidean(...) ASC`、必须 `LIMIT`、不能 JOIN、`WHERE` 不能用 `sortColumns` 中的列、不能 `GROUP BY/HAVING`。
- **IMOLTP 当前版本不支持分区也不支持 DDL 事务**：`partitionType` / `partitionScheme` 只为接口一致性保留，无实际作用；`transaction` 块内仅支持 DML。
- **PKEY 分区列影响写入性能**：递增 ID 或带日期的唯一 ID 直接当分区列会让写入分散到大量分区，需用分区转换函数（如 `myPartitionFunc(id, 6, 8)`）从中提取日期再分区。

## 下钻原文

- `official/db_distr_comp/db/tsdb.md` — TSDB 引擎详解（LSM-Tree、sortColumns、Level File、写入/查询/更新/删除流程、性能调优）
- `official/db_distr_comp/db/olap.md` — OLAP 列存引擎、Cache Engine、MVCC 事务
- `official/db_distr_comp/db/pkey_engine.md` — PKEY 主键引擎、Merge-on-Write、delete bitmap、bloomfilter/zonemap 索引
- `official/db_distr_comp/db/imoltp.md` — IMOLTP 内存 OLTP 引擎、B+ 树 OLC、MV2PL、WAL/Checkpoint、`createIMOLTPTable`
- `official/db_distr_comp/db/vectordb.md` — VectorDB 向量索引（Flat/PQ/IVF/IVFPQ/HNSW）、混合检索、Faiss 集成
- `official/db_distr_comp/db/tiered_storage.md` — 分级存储（热数据 volumes → 冷数据 coldVolumes / S3）
