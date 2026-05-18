# 数据导入

## 30 秒选型

| 场景 | 方法 | 优势 |
|---|---|---|
| 单文件 / dev 验证 | `loadText` → `tableInsert` | 简单 |
| 大文件（>1GB） | `textChunkDS` + `mr` | 分块流式，不爆内存 |
| 一天一文件，批量历史回填 | `loadTextEx` + `submitJob` 多并发 | 并行 |
| 海量小文件（每个股票一文件） | HASH 分桶合并 + `submitJob` | 减少小事务 |
| Python DataFrame → DDB | `TableAppender` / `PartitionedTableAppender` | 自动类型转换 |
| 高频流式写入 | `MultithreadedTableWriter` | C++ 后台批量 |

## DDB Script 三种导入

### 方式 1：loadTextEx（推荐，按日切文件）

```dolphindb
dataPath = "/data/snapshot/"            // 一天一文件
file_list = files(dataPath).filename
dbName = "dfs://stock_lv2_snapshot"
tbName = "snapshot"

// 用现有表 schema 解析（保证类型一致）
schema = select name, typeString as type
         from loadTable(dbName, tbName).schema().colDefs

def loadDataByDay(dbName, tbName, schema, fileName){
    loadTextEx(
        dbHandle=database(dbName), tableName=tbName,
        partitionColumns=["TradeDate", "SecurityID"],
        filename=fileName, schema=schema,
        sortColumns=[`SecurityID, `TradeTime]
    )
}

def submitLoad(dbName, tbName, schema, fileName){
    submitJob("loadDay", "load " + fileName,
              loadDataByDay, dbName, tbName, schema, fileName)
}

// 串行（社区版 4 worker，4 个并发就够了）
each(submitLoad{dbName, tbName, schema}, dataPath + file_list)

// 看进度
getRecentJobs(size(file_list))
```

### 方式 2：textChunkDS + mr（大文件不爆内存）

```dolphindb
// 512 MB 一块
ds = textChunkDS(fileName=dataPath+"huge_file.csv",
                 chunkSize=512, schema=schema)

// parallel=false：每块串行写（多线程并发写同一 DFS 表会冲突）
mr(ds, tableInsert{loadTable(dbName, tbName)}, parallel=false)
```

**关键**：`parallel=false` 不能省。多 worker 并发写同一分区会触发锁等待，反而更慢。

### 方式 3：海量小文件按 HASH 合并

```dolphindb
// 每个股票一个 csv，5000 个文件 → 合成 50 个批次
tmp = table(file_list as path, file_list.split(".")[0] as sid)
update tmp set hashNo = sid.hashBucket(50)
batches = select toArray(path) as fileBucket from tmp group by hashNo

def loadBatch(dbName, tbName, schema, fileNames){
    bigTable = loop(loadText{schema=schema}, fileNames).unionAll()
    return loadTable(dbName, tbName).tableInsert(bigTable)
}

for(i in 0:batches.size()){
    submitJob("loadBatch_" + string(i), "load hash " + string(batches.hashNo[i]),
              loadBatch, dbName, tbName, schema, dataPath + batches.fileBucket[i])
}
```

## 数据预处理（导入时变换）

### 时间格式转换

```dolphindb
// CSV 时间列是字符串 "09:30:00.000 04/01/2022"
schema = extractTextSchema(dataPath)
update schema set type = "STRING" where name = "tradetime"

def transFunc(mutable msg){
    msg.replaceColumn!("tradetime",
        msg.tradetime.temporalParse("HH:mm:ss.SSS dd/MM/yyyy"))
    return msg
}

loadTextEx(dbHandle=database(dbName), tableName=tbName,
           partitionColumns="tradetime",
           filename=dataPath, schema=schema,
           transform=transFunc)
```

### 从文件名提取字段

```dolphindb
// 文件名是股票代码，要加进表里
def transFunc(mutable msg, sid, orderCols){
    data = select sid as SecurityID, * from msg
    data.reorderColumns!(orderCols)
    return data
}

orderCols = loadTable(dbName, tbName).schema().colDefs.name

for(i in 0:sids.size()){
    loadTextEx(..., transform=transFunc{, sids[i], orderCols})
}
```

### 多列合并成数组向量（10 档行情）

```dolphindb
def transFunc(mutable msg){
    return select TradeDate, TradeTime, SecurityID,
        fixedLengthArrayVector(offerPx1, offerPx2, ..., offerPx10) as offerPx,
        fixedLengthArrayVector(bidPx1, bidPx2, ..., bidPx10) as bidPx
    from msg
}
```

## Python SDK 四种写入方式

### 1. tableInsert（一次性小批量）

```python
import pandas as pd

s.run("t = table(100:0, [`code`,`price`], [SYMBOL, DOUBLE])")
data = pd.DataFrame({'code': ['600000','600036'], 'price': [10.5, 35.2]})
s.run("tableInsert{t}", data)
```

适合：内存表 / 单次少量数据。

### 2. TableAppender（自动类型转换）

```python
import dolphindb as ddb

appender = ddb.TableAppender(
    dbPath="dfs://stock_lv2_snapshot",
    tableName="snapshot",
    ddbSession=s,
)
rows = appender.append(df)   # df 是 pd.DataFrame
```

适合：DataFrame → DDB 单连接顺序写。**不需要手动管理列类型映射**。

### 3. PartitionedTableAppender（并发写分区表，**推荐**）

```python
pool = ddb.DBConnectionPool("localhost", 8848, threadNum=3,
                             userId="admin", password="123456")

ptAppender = ddb.PartitionedTableAppender(
    dbPath="dfs://stock_lv2_snapshot",
    tableName="snapshot",
    partitionColName="SecurityID",     // Python SDK 用普通字符串，不要写反引号
    dbConnectionPool=pool,
)
rows = ptAppender.append(df)
pool.shutDown()
```

适合：DataFrame → DFS 分区表的**主流方式**。`partitionColName` 必须是表的分区列之一，pool 会按 hash 分发到不同连接并发写。

**社区版 4 worker → pool size 3**（留 1 个给 web/管理）。

### 4. MultithreadedTableWriter（高频流式写入）

```python
writer = ddb.MultithreadedTableWriter(
    "localhost", 8848, "admin", "123456",
    dbPath="dfs://stock_lv2_snapshot",
    tableName="snapshot",
    batchSize=10000,            // 攒 1w 行批量发
    throttle=1,                 // 或最多攒 1s
    threadCount=2,              // 后台线程数
    partitionCol="SecurityID",
)

for record in tick_stream:
    writer.insert(*record)      // 逐条插入，writer 自己批

writer.waitForThreadCompletion()
status = writer.getStatus()
```

适合：实时行情、kafka 消费等高频场景。后台 C++ 线程不受 Python GIL 限制。

**坑**：`insert(*args)` 参数顺序必须和表列顺序一致，写错只在线程里报错，主线程不感知。要看 `writer.getStatus()` 确认。

## 批量写入硬限（**Python 端必守**）

```python
BATCH_SIZE = 500_000   // TSDB 单次 append ≤ 204MB（约 800K 行 × 30 列），500K 行 ≈ 120MB 安全余量
```

| 规则 | 原因 |
|---|---|
| 每批 ≤ 500K 行 | TSDB 单次 append 内存上限 204MB，超出报 `exceeds max limit` |
| 每批后 `gc.collect()` | 释放 Python 侧 DataFrame 内存 |
| 每批后 `del batch_df` | 显式释放引用 |
| 大文件用 pyarrow 分片 | `pf.read_table()` memory-mapped，不全量加载 |
| 批量循环复用同一 Session | 不要每批新建/关闭连接 |

### 标准范式：pyarrow + slice 分片

```python
import pyarrow.feather as pf
import gc

table = pf.read_table("10M_rows.ftr")          # memory-mapped，不全量读入 RAM
appender = ddb.TableAppender(dbPath="dfs://x", tableName="t", ddbSession=s)

num_batches = (table.num_rows + BATCH_SIZE - 1) // BATCH_SIZE
for i in range(num_batches):
    arrow_slice = table.slice(i * BATCH_SIZE, BATCH_SIZE)
    batch_df = arrow_slice.to_pandas()
    del arrow_slice
    appender.append(batch_df)
    del batch_df
    gc.collect()
```

### 禁止的写法

```python
# ❌ 一次性读取大文件到 pandas（10M 行 ≈ 2.6GB，OOM）
df = pd.read_feather("10M_rows.ftr")

# ❌ 单次 append 超过 500K 行
appender.append(df_1million_rows)              # 直接报 exceeds max limit

# ❌ 循环不释放内存
for batch in batches:
    appender.append(batch)
    # 忘记 del + gc.collect() → 累积到 8GB OOM
```

## 性能基线（2核8G 社区版参考）

| 方式 | 吞吐 |
|---|---|
| loadText（单线程） | 100-200 MB/s |
| loadTextEx + submitJob × 4 | 300-500 MB/s |
| TableAppender | 50-100 万行/s |
| PartitionedTableAppender + pool 3 | 200-400 万行/s |
| MultithreadedTableWriter | 500-1000 万行/s |

## 常见报错

| 报错 | 原因 | 处理 |
|---|---|---|
| `Data conversion error: column X` | DataFrame 列类型对不上 | 用 `df[col].astype(...)` 转好；或换 `TableAppender` 自动转 |
| `Out of memory` | 单批太大 | DataFrame 切片：`for chunk in np.array_split(df, 10): appender.append(chunk)` |
| `Partition does not exist` | VALUE 分区还没建 | 库要开 `allowMissingPartitions=true` 或预建好分区 |
| `loadTextEx` 卡住 | 文件被 office 锁住 / 编码问题 | `extractTextSchema()` 看是否能正确识别 |
| 写入很慢 | 多 worker 写同一分区抢锁 | `parallel=false`（DDB Script）或按分区列分发（Python） |

跨引用：建表 → [[create-database-table]]，查询 → [[crud-operations]]，调优 → [[performance-tuning]]。
