# 变更检查清单

> 何时引用：写新 DDB 代码 / 改 DDB 代码 / SQL / Python SDK 调用前，按清单逐条自检。
> 来源：dwy-dolphindb skill 内部规则。

## 写 / 改 DDB 代码前过一遍

- [ ] WHERE 是否命中分区列？分区列是否被函数包裹（`year()` / `date()` / `temporalAdd()`）？
- [ ] 范围条件用了 `between ... and ...` 或两个独立条件？没有链式比较 `a <= col <= b`？
- [ ] 单次 `append` ≤ 500K 行？循环里有 `del + gc.collect()`？
- [ ] 大文件用 pyarrow `read_table + slice`，不是 `pd.read_feather` 全量加载？
- [ ] 拼接 DDB 脚本时，外部输入有正则白名单校验？（防注入）
- [ ] `pool.run()` 用 `await`（原生 async），`Session.run()` 用 `asyncio.to_thread()`？
- [ ] 连接池大小 ≤ CPU 核数 × 2（社区版 4 worker → pool 3）？
- [ ] `select` 只取需要的列？没有 `select *`？
- [ ] 多次聚合查询能否合并为一次？
- [ ] 多因子横向查询用了 `pivot by`，不是 Python 端 merge？
- [ ] backtick 列名定义在单行内？
- [ ] 分页用 `limit offset, count`（**不是** `LIMIT x OFFSET y`）？
- [ ] 新建库表：单分区估算大小落在引擎区间？总分区数远低于 65536？二级高基数列走 `HASH` 不是 `VALUE`？
- [ ] 写入 SYMBOL 列前校验 ≤ 255 字节？STRING/BLOB 有长度断言防静默截断？
- [ ] 删数据用 `dropPartition`，不是 `delete from`？
- [ ] pandas → DDB：`uint` 是否 `.astype('int64')`？NaN→int 是否 `.fillna(0)`？
- [ ] Session / Pool 有 `try/finally close()`？

## 慢查询 5 分钟排查清单

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

## 杀作业

```dolphindb
// 同步作业（getConsoleJobs 找到 rootJobId）
cancelConsoleJob(`xxxxxxxx)

// 异步作业（getRecentJobs 找到 jobId）
cancelJob(`yyyyyyyy)

// 取消是设置标志，不立即生效，再过几秒看是否结束
```

跨引用：致命违规 → [[lethal-violations]]，反模式细节 → [[anti-patterns]]，性能基线 → [[perf-baselines]]。
