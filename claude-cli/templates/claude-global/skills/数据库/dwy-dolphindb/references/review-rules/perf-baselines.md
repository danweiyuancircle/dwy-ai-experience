# 性能基线（DolphinDB 3.0 社区版 2 核 8G）

> 何时引用：评估查询/写入性能、判断是否需要优化、配置 dolphindb.cfg。
> 来源：dwy-dolphindb skill 内部规则 + 社区版实测数据。

## 资源预算（死守）

```
总内存 8 GB
├── OS + DDB 自身                 ~1 GB
├── chunkCache + 索引             ~1.5 GB
├── 4 个 worker 缓冲              ~1.5 GB
├── 留给单查询的预算              ≤ 2 GB ← 任何 SELECT/计算别超
└── 安全冗余                      ~2 GB

CPU 2 核 → worker 4 → 实际并发能力 ≤ 4
```

**查询前估算**：

```dolphindb
// 估这个查询要多大内存
select count(*) * 1000 / 1024 / 1024 as mb_estimate    // 假设每行 1KB
from loadTable("dfs://x", "t")
where TradeDate between 2024.01.01 and 2024.01.05
```

行数 × 列宽 > 2GB → 必须分批 / mr / 分页。

## 配置调优（社区版 dolphindb.cfg）

社区版固定 2 核 8G，可调的关键参数：

| 参数 | 建议值 | 说明 |
|---|---|---|
| `maxMemSize` | 6 (GB) | 节点最大内存，留 2GB 给 OS |
| `workerNum` | 4 | worker 线程数 = CPU 核数 × 2 |
| `localExecutors` | 3 | 本地并发执行器 |
| `chunkCacheEngineMemSize` | 1 (GB) | 列缓存，太大挤压查询内存 |
| `TSDBCacheEngineSize` | 0.5 (GB) | TSDB 写缓存 |
| `webWorkerNum` | 1 | Web UI 用，留 1 个够 |

**修改方式**：编辑配置文件 → 重启集群。或运行时 `setMaxMemSize(...)`（部分参数支持热改）。

## 性能基线对标

| 操作 | 2 核 8G 社区版 |
|---|---|
| 单股单天 tick 点查 | < 100ms |
| 单股一月 tick 扫描 | 1-3s |
| 全市场单日聚合（5000 股） | 3-10s |
| K 线合成（1 个月 + 1000 股） | 30-60s |
| 因子计算（截面 z-score，1 月） | 10-30s |
| Python 拉 100 万行 → DataFrame | 2-5s |
| `PartitionedTableAppender` 写入 | 200-400 万行/s |

**超过基线 2-3x 必须排查**：剪枝是否生效（`select [HINT_EXPLAIN]`）、索引是否覆盖、并发是否争抢同分区。

## 分区粒度目标

| 引擎 | 单分区压缩后目标 |
|---|---|
| TSDB | 400 MB - 1 GB |
| OLAP | 100 MB - 300 MB |

总分区数 < 65536，否则触达 `maxPartitionNumPerQuery` 上限。

## 连接池大小

| 资源 | 建议值 |
|---|---|
| CPU 核数 | 2 |
| workerNum | 4 |
| `DBConnectionPool` size | **3** |
| Session 上限（节点） | 512 |

跨引用：致命违规 → [[lethal-violations]]，反模式细节 → [[anti-patterns]]，变更前自检 → [[change-checklist]]。
