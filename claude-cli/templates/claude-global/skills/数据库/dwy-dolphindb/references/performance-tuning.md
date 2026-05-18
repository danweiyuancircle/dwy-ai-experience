# 性能排查与调优

## 社区版 2核8G 资源预算（**死守**）

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

## 5 分钟排查清单

按顺序执行：

```dolphindb
// 1. 集群整体（看 CPU/内存/磁盘）
getClusterPerf()

// 2. 所有节点的同步作业（用户正在跑的查询）
pnodeRun(getConsoleJobs)

// 3. 最近 20 个异步作业
getRecentJobs(20)

// 4. 当前 session 内存
getSessionMemoryStat()

// 5. 整机内存细节
getMemoryStat()

// 6. 磁盘 IO
getDiskIOStat()

// 7. 看慢查询用了哪些分区
select [HINT_EXPLAIN] * from loadTable(dbName,tbName) where 你的条件
```

## 监控命令速查

| 命令 | 用途 | 输出关键列 |
|---|---|---|
| `getClusterPerf()` | 集群整体 | name, mode, host, port, memUsed, cpuUsage |
| `getPerf()` | 单节点 | 同上单节点版 |
| `getConsoleJobs()` | 同步作业（用户当前查询） | rootJobId, sessionId, userId, startTime, jobDesc |
| `pnodeRun(getConsoleJobs)` | **所有节点**的同步作业 | 同上 |
| `getRecentJobs(n)` | 最近 n 个异步作业 | jobId, status, startTime, endTime, errorMsg |
| `getJobStatus(jobId)` | 单个异步作业状态 | status, progress |
| `getJobMessage(jobId)` | 异步作业日志 | print 出的内容 |
| `getJobReturn(jobId)` | 异步作业返回值 | 计算结果 |
| `getSessionMemoryStat()` | 各 session 内存 | sessionId, memSize, lastActiveTime |
| `getMemoryStat()` | 节点内存细节 | shared array memory, chunk cache 等 |
| `getDiskIOStat()` | 磁盘 IO | read/write speed, IOPS |
| `getTableDiskUsage(db, tb)` | 表磁盘占用 | size per partition |
| `getClusterChunksStatus()` | 分区分布 | chunkPath, state, version |
| `getAllChunks()` | 所有 chunk | 同上详细版 |

## 杀作业

```dolphindb
// 同步作业（getConsoleJobs 找到 rootJobId）
cancelConsoleJob(`xxxxxxxx)

// 异步作业（getRecentJobs 找到 jobId）
cancelJob(`yyyyyyyy)

// 取消是设置标志，不立即生效，再过几秒看是否结束
```

## 慢查询排查流程

```
1. 加 [HINT_EXPLAIN] 看是否分区剪枝
   ├── 没剪枝 → 改 WHERE（见 crud-operations.md）
   └── 剪枝了但还慢 ↓
2. 查 getConsoleJobs：是不是被其他作业抢资源
   ├── 是 → 排队 / 降优先级
   └── 否 ↓
3. 查 getDiskIOStat：是不是磁盘瓶颈
   ├── 是 → 减少扫描分区 / 升 SSD
   └── 否 ↓
4. 查 getSessionMemoryStat：内存是否爆
   ├── 是 → 拆批 / mr / fetchSize 分页
   └── 否 ↓
5. 查 schema：sortColumns 是否覆盖 WHERE 条件
   └── 不覆盖 → 重建表（TSDB sortColumns 不能改）
```

## 常见性能问题

### 问题 1：查询返回慢

**症状**：`select` 跑 30 秒+ 才返回。

**排查**：
```dolphindb
select [HINT_EXPLAIN] * from t where ...
```

输出里看 `PartitionInfo`：
- 扫描分区数 ≈ 总分区数 → 没剪枝
- 扫描分区数 = 预期 → 看 `scannedRows`

**修复**：
- 没剪枝 → WHERE 用分区列直接等于/between
- 数据量太大 → 服务端先聚合再返回（`group by` 而不是 `select *`）

### 问题 2：写入慢

**症状**：`tableInsert` 1 万行要 10 秒。

**排查**：
```dolphindb
pnodeRun(getConsoleJobs)         // 是否多个写并发抢同一分区
getDiskIOStat()                  // 磁盘是否饱和
```

**修复**：
- 多 worker 抢同一分区 → 改成 `PartitionedTableAppender` 按分区列分发
- 单连接 → 用 `DBConnectionPool` size 3
- 索引膨胀（TSDB） → 看 `getTableDiskUsage`，索引大于数据 = sortColumns 选错了

### 问题 3：OOM (Out of memory)

**症状**：报 `Out of memory`，节点重启。

**根因排查**：
```dolphindb
getMemoryStat()                  // 看哪部分占内存
getSessionMemoryStat()           // 哪个 session 持有大对象
```

**常见原因 + 修复**：
| 原因 | 修复 |
|---|---|
| 单查询拉太多数据 | Python 端 `fetchSize=8192` 分段拉 |
| 服务端 `context by` 大表 | 改 `mr` 按分区计算 |
| 客户端 `df = s.run("select *")` | 改 `group by` 服务端聚合 |
| 大批量 import 没拆 | 切成 100MB 一批 |
| `pivot by` 产生超大矩阵 | 先过滤再 pivot |

### 问题 4：节点卡死 / 无响应

**应急**：
1. 另起 session（用 controller 端口 8848）
2. `getClusterPerf()` 看哪个节点 mem 100%
3. `rpc("nodeX", getConsoleJobs)` 查那个节点的作业
4. `rpc("nodeX", cancelConsoleJob, jobId)` 杀掉
5. 如果完全卡死 → 安全重启该节点（不是 kill -9）

**预防**：startup 脚本里加：
```dolphindb
// 自动清理超时 session
addJob("session_cleanup", "kill idle sessions", {def(){
    sessions = getSessionMemoryStat()
    idle = select sessionId from sessions where lastActiveTime < now() - 3600*1000
    each(closeSession, idle.sessionId)
}}, 0, 1, `hour)
```

### 问题 5：磁盘要满了

**监控**：
```dolphindb
// 各表占用
select * from getTableDiskUsage(getClusterDFSDatabases()[0])

// 整库
select sum(diskUsage) as totalGB from (
    each(getTableDiskUsage, getClusterDFSDatabases())
)
```

**清理**：
- 旧分区 `dropPartition` 删除（按日期）
- TSDB 的 redo log 自动清理，但磁盘满会卡写
- chunk cache 设上限：`chunkCacheEngineMemSize=1` (GB)

## 配置调优（社区版 dolphindb.cfg）

社区版固定 2核8G，可调的关键参数：

| 参数 | 建议值 | 说明 |
|---|---|---|
| `maxMemSize` | 6 (GB) | 节点最大内存，留 2GB 给 OS |
| `workerNum` | 4 | worker 线程数 = CPU 核数 × 2 |
| `localExecutors` | 3 | 本地并发执行器 |
| `chunkCacheEngineMemSize` | 1 (GB) | 列缓存，太大挤压查询内存 |
| `TSDBCacheEngineSize` | 0.5 (GB) | TSDB 写缓存 |
| `webWorkerNum` | 1 | Web UI 用，留 1 个够 |

**修改方式**：编辑配置文件 → 重启集群。或运行时 `setMaxMemSize(...)`（部分参数支持热改）。

## 性能基线（参考）

| 操作 | 2核8G 社区版 |
|---|---|
| 单股单天 tick 点查 | < 100ms |
| 单股一月 tick 扫描 | 1-3s |
| 全市场单日聚合（5000股） | 3-10s |
| K 线合成（1 个月 + 1000 股） | 30-60s |
| 因子计算（截面 z-score, 1 月） | 10-30s |
| Python 拉 100 万行 → DataFrame | 2-5s |
| PartitionedTableAppender 写入 | 200-400 万行/s |

超过基线 2-3x 必须排查（剪枝、索引、并发）。

跨引用：建表选型 → [[create-database-table]]，查询写法 → [[crud-operations]]。
