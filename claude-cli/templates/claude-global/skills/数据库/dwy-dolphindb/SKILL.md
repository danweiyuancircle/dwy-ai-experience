---
name: dwy-dolphindb
description: "DolphinDB 3.0 社区版（2核8G / 1控2节点）开发与审查 skill：写 DolphinDB Script (.dos)、用 Python SDK (dolphindb 3.0.4)、设计 DFS 分区表（TSDB/OLAP 引擎选型）、导入 tick/snapshot/kline 金融数据、优化慢查询、排查 OOM / 卡死作业、Docker 部署。也用于代码审查：检查分区裁剪（链式比较 `a <= col <= b`、函数包裹分区列）、批量写入 ≤500K 行、SYMBOL ≤255 字节、STRING/BLOB 静默截断、输入校验防脚本注入、连接池配置、`pool.run` async/sync 用法。关键字触发：dolphindb, DDB, loadTable, loadTextEx, createPartitionedTable, append!, dropPartition, DBConnectionPool, tableAppender, PartitionedTableAppender, MultithreadedTableWriter, addRangePartitions, newValuePartitionPolicy, TSDB, OLAP, getClusterPerf, getConsoleJobs, level2 行情, tick 数据, 时序数据库, 8848 端口, .dos 脚本."
---

# DolphinDB 3.0 社区版使用指南

## 当前环境

| 项 | 值 |
|---|---|
| 版本 | DolphinDB 3.0 社区版 |
| 拓扑 | 1 控制节点 + 2 计算/数据节点 |
| 资源 | 2 核 / 8GB 内存（已分配 3GB），磁盘 33 TB |
| 端口 | Web/控制 `http://localhost:8848`，集群另含 `192.168.0.107:8848` / `172.17.0.1:8848` 等 |
| Worker | 4 线程，连接上限 512（当前 15） |
| Python SDK | `dolphindb==3.0.4` |
| 场景 | 个人/小团队 + 教学，**单查询内存上限按 2GB 控制**（详见 [[performance-tuning]]）|

## 何时进入哪份 reference

| 你正在做 | 看这里 |
|---|---|
| 第一次连 DDB / `import dolphindb` 报错 / 8848 进不去 | [[setup-and-connection]] |
| 设计 DFS 分区表 / 选 TSDB 还是 OLAP / 给 level2 建表 | [[create-database-table]] |
| `loadText` 慢 / 想多线程导入 / Python 写 DataFrame 进 DDB | [[data-import]] |
| 写 SELECT/INSERT/UPDATE/DELETE / `delete` 删一整个分区 | [[crud-operations]] |
| 合成 K 线 / 算 SOIR 订单失衡 / 截面排名 / 用 `mr` 分布式跑批 | [[sql-batch-compute]] |
| Python SDK 用法 / `session.run` 高级参数 / 流订阅 / 异步写 / 类型映射 | [[python-api]] |
| 查询慢 / OOM / 节点卡住 / 内存涨不下来 / 不知道哪个作业在跑 | [[performance-tuning]] |
| 时间类型踩坑 / DECIMAL 精度 / SYMBOL 长度 / backtick 单行 / 反模式 | [[pitfalls-and-best-practices]] |
| Docker 部署 / Alpine 镜像坑 / healthcheck / 资源限制 | [[docker-deployment]] |
| 官方文档链接 / 版本基线 / GitHub 仓库 | [[sources]] |

## 30 秒速查

```dolphindb
// 连接（Python）
import dolphindb as ddb
s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")

// 看集群健康
s.run("getClusterPerf()")                       // CPU/内存/磁盘
s.run("getRecentJobs(20)")                      // 最近 20 个批作业
s.run("pnodeRun(getConsoleJobs)")               // 所有节点同步作业
s.run("getSessionMemoryStat()")                 // 当前 session 内存

// 看库表
s.run("getClusterDFSDatabases()")               // 所有 DFS 库
s.run("getClusterDFSTables('dfs://xxx')")       // 库下所有表
s.run("schema(loadTable('dfs://xxx','t'))")     // 表结构

// 杀作业（按 rootJobId）
s.run("cancelJob(`xxxx)")                       // 异步作业
s.run("cancelConsoleJob(`xxxx)")                // 同步作业
```

## 核心原则（社区版 2核8G 必须遵守）

1. **单查询不超 2GB**：8GB 内存 → 系统/缓存 2GB + worker 缓冲 2GB + 单查询预算 ≤ 2GB。先 `count()` 估行数 × 列宽，超了就走分区分批或 `mr`。
2. **任何 WHERE 必带分区列**：否则全表扫，2 节点直接 OOM。用 `select [HINT_EXPLAIN] ...` 验证是否触发分区剪枝。
3. **TSDB 排序列别选高基数**：`sortColumns` 不要用主键/唯一列（索引膨胀）；金融场景用 `[SecurityID, TradeTime]`。
4. **写入用 PartitionedTableAppender + DBConnectionPool**：单连接 + `tableInsert` 慢，4 worker → pool size 3。
5. **删数据按分区删**：`dropPartition()` 秒级，`delete from` 全表扫慢且占内存。

## 反模式（看到立即停手）

| 反模式 | 后果 | 改成 |
|---|---|---|
| `select * from t where 2024.01.01 <= TradeDate <= 2024.01.05` | 链式条件不触发剪枝 → 全表扫 | `where TradeDate between 2024.01.01 and 2024.01.05` |
| `delete from t where TradeDate=2024.01.01` | 重写整个分区，慢+占内存 | `dropPartition(database(dbName), 2024.01.01, tableName='t')` |
| 在客户端 `s.run("select * from huge_table")` | 一次拉全部，OOM | `s.run("...", fetchSize=8192)` 分段读 |
| DECIMAL 列用 FLOAT/DOUBLE | 精度丢失（金融场景禁用） | `DECIMAL32(3)` / `DECIMAL64(6)` |
| `DATETIME` 存 2038 后的时间 | 32 位 int 溢出 → 显示 1970 | 全用 `TIMESTAMP`（毫秒精度 64 位） |
| 建表时 `sortColumns` 用 UUID/序列号 | 索引膨胀，TSDB 查询变慢 | 用 `[业务键, 时间列]` 组合 |

**完整反模式清单**（类型陷阱 / SQL 陷阱 / 库表设计 / 写入 / 运维）见 [[pitfalls-and-best-practices]]。

## 审查模式（代码 review / CR 用）

任务是**审查**他人代码时，按以下格式输出：

```
⚠️ [reference名] 具体问题
   违规代码：<摘录>
   修复建议：<可直接替换的代码>
   原因：<对应 reference 里的依据，一句话>

✅ [reference名] 符合要求 — <简要说明>
```

### 10 条致命违规（零容忍）

| # | 违规 | 后果 |
|---|---|---|
| 1 | 分区列被函数包裹（`date(col)` / `year(col)` / `temporalAdd(col,...)`） | 全表扫 → OOM |
| 2 | 链式比较 `a <= col <= b` | 不触发剪枝 → 全表扫 |
| 3 | 单次 `append` > 500K 行 | TSDB 报 `exceeds max limit` |
| 4 | 未校验外部输入拼到脚本 | 脚本注入 |
| 5 | 连接池里 upload + run（变量跨连接不可见） | 变量找不到 |
| 6 | `select *`（30+ 列全传） | 浪费带宽和内存 |
| 7 | 分页用 `LIMIT x OFFSET y` | DDB 不支持 OFFSET 关键字 |
| 8 | `asyncio.to_thread(pool.run, script)` | SDK v3 `pool.run` 已是原生 async |
| 9 | SYMBOL 列写入未校验 ≤255 字节 | 整批写入失败 |
| 10 | 单分区 < 100MB 且总分区数 > 65536 | 触达 `maxPartitionNumPerQuery` 上限 |

完整审查清单 ↓

## 变更检查清单（写 / 改 DDB 代码前过一遍）

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

## 必读官方资料

完整源 URL 见 [[sources]]。常用 3 个：
- 金融入门：https://docs.dolphindb.cn/zh/tutorials/new_users_finance.html
- 使用须知：https://docs.dolphindb.cn/zh/tutorials/usage_guidelines.html
- Python SDK：https://docs.dolphindb.cn/zh/pydoc/ （3.0.4）
