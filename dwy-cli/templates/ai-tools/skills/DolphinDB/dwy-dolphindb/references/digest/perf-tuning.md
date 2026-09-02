---
topic: perf-tuning
source_files:
  - official/funcs/g/getClusterPerf.md
  - official/funcs/g/getConsoleJobs.md
  - official/funcs/g/getSessionMemoryStat.md
  - official/funcs/g/getMemoryStat.md
  - official/funcs/c/cancelJob.md
generated_at: 2026-05-19
---

# 性能调优

## 何时用此主题

- 节点慢/卡，需要定位是 CPU、内存、磁盘还是网络瓶颈
- 查询 RT 突增，需要找出慢 SQL/慢作业并杀掉
- 频繁 OOM、`Out of memory` 错误
- 写入吞吐下降、`flushTSDBCache` 阻塞、redo log 堆积
- 集群容量规划（磁盘 80%、内存 70% 告警阈值）

## 1. 资源监控速查表

所有命令优先用 `pnodeRun(funcName)` 批量打到所有数据节点。

| 维度 | 函数 | 关键字段 | 用途 |
| --- | --- | --- | --- |
| 集群总览 | `getClusterPerf(true)` | memoryUsed/cpuUsage/avgLoad/runningJobs/queuedJobs/diskFreeSpaceRatio | 一次性看所有节点的 CPU、内存、磁盘、作业队列 |
| 活跃作业 | `getConsoleJobs()` | rootJobId/desc/priority/parallelism/firstTaskStartTime/queue | 看本地节点正在跑的交互式作业 |
| 全集群作业 | `pnodeRun(getConsoleJobs)` | 同上 | 看所有数据节点的活跃作业 |
| 历史作业 | `getRecentJobs([n])` | jobId/startTime/endTime/errorMsg | 看最近 n 条批作业（含已完成/失败） |
| 节点内存 | `getMemoryStat()` | allocatedBytes/freeBytes | 节点已分配/未使用内存（差值=占用） |
| 会话内存 | `getSessionMemoryStat()` | userId/sessionId/memSize | 哪个会话/哪个引擎吃内存（含 OLAP/TSDB CacheEngine、共享表、维度表、流队列） |
| 磁盘 IO | `getDiskIOStat()` | readRate/writeRate/IOPS | 看磁盘读写速率 |
| 表磁盘占用 | `getTableDiskUsage(dbUrl, tbName)` | size | 单表占用空间，找异常大表 |
| chunk 状态 | `getClusterChunksStatus()` | chunkId/state/version | 看 chunk 是否健康、版本是否一致 |

速查脚本：

```dolphindb
// 一行体检
select name, memoryUsed/1024/1024/1024 as memGB, cpuUsage, runningJobs, queuedJobs,
       diskFreeSpaceRatio
from pnodeRun(getClusterPerf) order by memGB desc

// 找吃内存的会话
select * from pnodeRun(getSessionMemoryStat) order by memSize desc limit 20

// 找跑得最久的活跃作业
select * from pnodeRun(getConsoleJobs) order by firstTaskStartTime asc limit 20
```

## 2. 慢查询定位流程

1. 加 `HINT_EXPLAIN` 看物理计划：`select [HINT_EXPLAIN] ... from pt where ...` — 看是否走分区剪枝、是否走 sortColumns 索引
2. 检查分区剪枝：where 条件必须命中分区字段；range/value 分区不剪枝时全表扫
3. 资源争抢：`getConsoleJobs` 看是否同时有大批作业占满 workerNum
4. 磁盘：`getDiskIOStat` 看 readRate 是否打满 IOPS，TSDB 大查询会读 level file
5. 内存：`getSessionMemoryStat` 看 `__TSDBCacheEngine__` / `__OLAPCacheEngine__` 是否爆了
6. sortColumns：TSDB 表查询必须带 sortColumns 前缀字段才走索引，否则全分区扫
7. 看 `getClusterPerf` 的 `medLast10QueryTime` / `maxRunningQueryTime`（需 `perfMonitoring=1`）

## 3. OOM 排查表

| 现象 | 常见原因 | 修复 |
| --- | --- | --- |
| `Out of memory, used XX, limit YY` | `maxMemSize` 设置过小 | 调大 `maxMemSize`，单节点建议物理内存 70% |
| 单会话 memSize 飙到几十 GB | 查询返回结果未分页/`select *` 全表拉回 | 加 LIMIT、用 `loop`/`each` 分批 |
| `__TSDBCacheEngine__` 巨大 | 写入未及时刷盘 | 调小 `TSDBCacheEngineSize`，或主动 `flushTSDBCache()` |
| `__OLAPCacheEngine__` 巨大 | OLAP 写入缓存堆积 | 调小 `chunkCacheEngineMemSize`，或调小 `cacheEngineLowWaterLevelRatio` |
| `__SharedTable__` 巨大 | 共享表/流表无限增长 | 设置 `enableTableShareAndPersistence` keepDuration 自动清理 |

## 4. 关键配置项

| 配置 | 含义 | 经验值 |
| --- | --- | --- |
| `maxMemSize` | 节点内存上限（GB） | 物理内存 70% |
| `workerNum` | 常规作业线程数 | CPU 核数 |
| `localExecutors` | 本地执行线程数 | CPU 核数 - 1 |
| `chunkCacheEngineMemSize` | OLAP Cache Engine 上限（GB） | maxMemSize 的 1/4 |
| `TSDBCacheEngineSize` | TSDB Cache Engine 上限（GB） | maxMemSize 的 1/8~1/4 |
| `redoLogPurgeInterval` | redo log 清理间隔（秒） | 30 |
| `dataSync` | redo log 落盘策略 | 1=每事务 fsync，强一致；0=异步，性能高 |

## 5. 杀作业

```dolphindb
// 杀交互式作业（getConsoleJobs 的 rootJobId）
cancelConsoleJob(rootJobId)

// 杀批处理作业（submitJob 返回的 jobId）
cancelJob(jobId)              // 单个
cancelJob(["jobId1", "jobId2"])  // 批量

// 一键清理全集群所有未完成批作业
def cancelAllBatchJob(){
   jobids = exec jobid from getRecentJobs() where endTime=NULL
   cancelJob(jobids)
}
pnodeRun(cancelAllBatchJob)
```

权限：管理员可杀任意用户作业；普通用户只能杀自己的（2.00.11+）。

## 6. 写入慢排查

| 现象 | 原因 | 修复 |
| --- | --- | --- |
| `tableInsert` RT 抖动 | 单线程写大批量 | 用 `PartitionedTableAppender` 多线程并发写 |
| TSDB 写入越来越慢 | sortColumns 维度过多导致 level file 索引膨胀 | sortColumns 维度数 ≤ 3，高基数字段放最后 |
| `redo log full` | 磁盘 IOPS 不够 | redo log 单独挂 SSD，或调大 `redoLogPurgeInterval` |
| 写入卡住、`flushTSDBCache` 阻塞 | TSDBCacheEngine 满 | 调大 `TSDBCacheEngineSize` 或加 `flushTSDBCache()` 主动刷 |
| OLAP 写入慢 | chunk 版本冲突 | 检查 `getClusterChunksStatus` 是否有 inconsistent |

## 7. 磁盘 80% 监控

```dolphindb
// 告警脚本：磁盘可用空间 < 20%
select name, diskFreeSpaceRatio
from pnodeRun(getClusterPerf)
where diskFreeSpaceRatio < 0.2
```

策略：

- TSDB 表设 TTL 自动清理：`setRetentionPolicy(db, hours, partitionColumnIndex)`
- 冷数据归档到 OSS/S3：`backup` + `restore`
- 单分区过大时考虑 COMPO 分区拆分

## 下钻

- `references/official/funcs/g/getClusterPerf.md` — 集群性能字段完整列表（含 perfMonitoring=1 才返回的字段）
- `references/official/funcs/g/getConsoleJobs.md` — 活跃作业字段、queue 类型说明
- `references/official/funcs/g/getSessionMemoryStat.md` — 内置缓存标识符（`__OLAPCacheEngine__` 等）完整含义
- `references/official/funcs/g/getMemoryStat.md` — allocatedBytes/freeBytes 字段
- `references/official/funcs/g/getRecentJobs.md` — 历史批作业查询
- `references/official/funcs/g/getDiskIOStat.md` — 磁盘 IO 速率
- `references/official/funcs/g/getTableDiskUsage.md` — 单表磁盘占用
- `references/official/funcs/g/getClusterChunksStatus.md` — chunk 状态
- `references/official/funcs/c/cancelJob.md` — 批作业取消（含 pnodeRun 全集群清理示例）
- `references/official/funcs/c/cancelConsoleJob.md` — 交互式作业取消
