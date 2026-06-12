---
topic: python-sdk
source_files:
  - official/pydoc/BasicOperations/Session/Connect.md
  - official/pydoc/BasicOperations/connection_pool.md
  - official/pydoc/BasicOperations/table_append.md
  - official/pydoc/BasicOperations/async_write.md
  - official/pydoc/BasicOperations/Subscription/Subscription.md
generated_at: 2026-05-19
---
# Python SDK 核心

## 何时用此主题

Python 应用接入 DolphinDB：建连、连接池、批量写入、流订阅、异步提交、Python ↔ DDB 类型映射、大结果分段拉取。优先看本摘要选型与陷阱，写真实代码前下钻原文确认参数。

## 安装与版本

- 包名 `dolphindb`，建议固定 `3.0.4`（与 server 主线 2.00.10+ 配套）。
- `pip install dolphindb==3.0.4`，Python 3.8–3.11；arm64 mac 走 conda 或源码。
- API 版本须匹配 server：1.30.x / 2.00.9 之前订阅需指定本地端口；2.00.9+ 反向推送，端口参数忽略。

## session.connect 关键参数

| 参数 | 说明 |
|---|---|
| host / port | 节点地址与端口（必填） |
| userid / password | 登录账号；也可 `s.login()` 二次登录 |
| highAvailability | True 开 API 高可用，自动重连 |
| highAvailabilitySites | `["ip:port", ...]`，未填则用集群全部节点 |
| keepAliveTime | TCP 保活秒数，默认 60，弱网下调大可及时释放半打开连接 |
| reconnect | 非高可用模式下断线自动重连开关 |
| tryReconnectNums | 重连尝试次数，缺省无限 |
| readTimeout / writeTimeout | TCP 读写超时（秒），缺省无限 |
| startup | 连接成功后执行的启动脚本（如 `clearAllCache();`、加载插件、定义流表） |
| protocol | 序列化协议，金融大批量优先 `PROTOCOL_DDB`；与 numpy/pandas 互操作可用默认 |

负载均衡公式：`load = (connectionNum + workerNum + executorNum) / 3.0`。多线程同时建连不能保证均衡，要么单线程错峰，要么客户端轮询。

## DBConnectionPool 用法

```python
from dolphindb import DBConnectionPool
pool = DBConnectionPool("localhost", 8848, 8, "admin", "123456")
task_id = 1
pool.addTask("select count(*) from loadTable('dfs://k', 'tick')", taskId=task_id)
df = pool.getData(taskId=task_id)
pool.shutDown()
```

- `size` 建议 = CPU 核数到 `2 × 核数`，跨节点查询可加大到 16；不是越大越好，server 端 workerNum 才是真瓶颈。
- `pool.run(script)` 在内部线程上跑，**返回的是协程（awaitable）**，必须 `await pool.run(...)`，**不要**再套 `asyncio.to_thread`，会双层线程化导致死锁/吞吐崩。
- `pool` 的 upload 与单 session 的 upload 不互通：连接池每条任务可能走不同物理连接，上传到一个连接的变量在另一个连接不可见。要共享变量改用单 session 或 server 端共享表（`share` / `streamTable`）。

## 写入方式选型

| 方式 | 适用场景 | 关键参数 | 是否多线程 |
|---|---|---|---|
| `tableAppender` | 中小批量、内存表/分布式表追加，需自动类型转换 | `dbPath, tableName, ddbSession` | 否 |
| `tableInsert` | 简单一次性 insert，server 端 `tableInsert(tbl, data)` | — | 否 |
| `PartitionedTableAppender` | 已知分区列、客户端并行按分区写入 dfs 表 | `dbPath, tableName, partitionColName, dbConnectionPool` | 是（按分区并发） |
| `MultithreadedTableWriter`（MTW） | 高吞吐流式写入（行情、订单流），自带缓冲 + 后台 flush + 失败重传 | `host, port, dbPath, tableName, useSSL, enableHighAvailability, highAvailabilitySites, batchSize, throttle, threadCount, partitionCol` | 是 |

经验：实时行情用 MTW；离线批 ETL 按分区切片用 PartitionedTableAppender；小批管理类数据用 tableAppender。

## 类型映射

| Python / pandas | DDB |
|---|---|
| `bool` | BOOL |
| `int8/16/32/64` | CHAR / SHORT / INT / LONG |
| `uint8/16/32/64` | 转 SHORT / INT / LONG / —（uint64 易溢出，建议强转 int64） |
| `float32/64` | FLOAT / DOUBLE |
| `str` | STRING |
| `bytes`(定长) | SYMBOL（建议显式 dtype） |
| `datetime64[ns]` | NANOTIMESTAMP |
| `datetime64[ms]` | TIMESTAMP |
| `datetime64[s]` | DATETIME |
| `datetime64[D]` | DATE |
| `Decimal` | DECIMAL32/64/128（须 server 端列已声明精度） |
| `np.nan` / `pd.NA` / `None` | NULL（DDB 用类型化 NULL，不要混用） |

upload DataFrame 时务必用 numpy dtype 明确化，禁止 `object`；时间列统一 `datetime64[ns]` 再让 server 端 cast。

## 大结果集分段

```python
res = s.runBlock("select * from loadTable('dfs://k','tick') where date=2026.05.19", fetchSize=100000)
while res.hasNext():
    df = res.read()      # 每次 10w 行
```

- 单条 `run` 默认一次传完，大结果会爆内存；`fetchSize` 强制分段。
- server 端单条 IPC 消息上限约 **500K 行**，超过会被截断/报错，配合 `fetchSize` 或 server 端分页。

## 流订阅

```python
import dolphindb as ddb, numpy as np
s = ddb.session()
s.enableStreaming()   # 2.00.9+ 反向推送，无需端口

def handler(msg):
    print(msg)        # batchSize 未设 → 单条 list；msgAsTable=True + batchSize → DataFrame

s.subscribe(
    host="localhost", port=8848,
    handler=handler,
    tableName="trades", actionName="py_sub",
    offset=-1,                       # -1 当前行；-2 从持久化 offset 续订
    resub=True, resubscribeInterval=100,
    filter=np.array(["000905"]),     # 或 lambda 字符串："msg -> select * from msg where sym=`000905"
    msgAsTable=True, batchSize=2000, throttle=1.0,
    backupSites=["192.168.1.3:8848"],
)

from threading import Event
Event().wait()
```

- 主题 = `host/port/tableName/actionName`，同 session 不可重名。
- 取消：`s.unsubscribe(host, port, tableName, actionName)`。
- backupSites 切换重连时，主备表结构与表名必须完全一致。

## 异步提交

```python
s = ddb.session(enableASYNC=True)    # 构造期开启异步
s.connect("localhost", 8848, "admin", "123456")
s.run("tableInsert{loadTable('dfs://k','tick')}", df)   # 立即返回，不阻塞结果回收
```

- 异步 session 的 `run` 返回 None，不可用于查询。
- 高吞吐写入优先用 MTW（已内置异步），异步 session 只在简单"发完即忘"日志/埋点场景用。

## 金融场景典型代码

### 1. 行情高频写入（MTW）

```python
import dolphindb as ddb
from dolphindb import MultithreadedTableWriter as MTW

writer = MTW(
    host="localhost", port=8848, userId="admin", password="123456",
    dbPath="dfs://market", tableName="tick",
    batchSize=20000, throttle=1.0, threadCount=4,
    partitionCol="symbol",
)
for row in feed:   # row: [ts, symbol, price, volume]
    writer.insert(*row)
writer.waitForThreadCompletion()
status = writer.getStatus()        # 检查 errorCode / sentRows
```

### 2. 分钟 K 线批量 ETL（PartitionedTableAppender）

```python
from dolphindb import DBConnectionPool, PartitionedTableAppender
pool = DBConnectionPool("localhost", 8848, 8, "admin", "123456")
appender = PartitionedTableAppender(
    dbPath="dfs://kline", tableName="min1",
    partitionColName="trade_date", dbConnectionPool=pool,
)
appender.append(df_min1)   # df 中 trade_date 列驱动并行
pool.shutDown()
```

## 常见陷阱

1. **`pool.run` 是原生协程**：`await pool.run(...)`，不要 `asyncio.to_thread(pool.run, ...)`，双线程化会卡死。
2. **pool upload 变量不可见**：连接池每个任务可能走不同物理连接，跨任务共享要走 server 端共享变量 / 共享表。
3. **session 必须显式 close**：长服务用 `try / finally s.close()`，否则 server 端 worker 不释放，重启服务后会被旧连接占满。
4. **单消息 500K 行上限**：批量 upload / `run` 超大 DataFrame 会被截断；分批 + `fetchSize`。
5. **uint 类型转换**：pandas 默认 `uint64` 上传到 DDB 会丢精度，先 `astype('int64')`。
6. **NaN ↔ NULL**：DDB NULL 是类型化的，`np.nan` 仅适用于 FLOAT/DOUBLE；INT 列要用 `pd.NA` 或 numpy nullable int (`Int64`)，否则上传成 0。
7. **订阅 batchSize 与 msgAsTable**：`msgAsTable=True` 必须配合 `batchSize > 0`，否则参数无效；若设了 `streamDeserializer`，`msgAsTable` 必须 False。
8. **多线程同时 connect 高可用模式**：服务端负载信息未同步，所有 session 落到同一节点；改单线程错峰建连或客户端二次轮询。
9. **enableStreaming 端口**：2.00.9 之前必须传端口且不能被占用；升级到 2.00.9+ 之前要先 unsubscribe，再升级，再重订。
10. **startup 脚本失败不抛**：构造期 startup 异常被吞，连上后立刻 `s.run("...")` 做一次显式自检。

## 下钻原文

- `references/official/pydoc/BasicOperations/Session/Connect.md` — connect 全参数表
- `references/official/pydoc/BasicOperations/connection_pool.md` — DBConnectionPool（目录页，详见同目录 connection_pool/）
- `references/official/pydoc/BasicOperations/table_append.md` — 三种写入对象对比（目录页）
- `references/official/pydoc/BasicOperations/async_write.md` — 异步写入三种方式对比（目录页）
- `references/official/pydoc/BasicOperations/Subscription/Subscription.md` — 订阅完整参数与示例
- `references/official/pydoc/AdvancedOperations/SubscriptionOptions/` — batchSize / msgAsTable / streamDeserializer 组合矩阵
