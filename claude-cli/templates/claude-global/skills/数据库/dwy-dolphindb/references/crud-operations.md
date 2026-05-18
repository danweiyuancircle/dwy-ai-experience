# 增删改查

## SELECT 基础

```dolphindb
dbName = "dfs://stock_lv2_snapshot"
tbName = "snapshot"
t = loadTable(dbName, tbName)

// 基本查询（WHERE 必带分区列！）
select * from t where TradeDate = 2024.01.03

// 字段处理
select concatDateTime(TradeDate, TradeTime) as ts,
       SecurityID,
       OfferPrice[0] as ask1,        // 数组向量取第 0 档
       BidPrice[0] as bid1,
       LastPrice
from t
where TradeDate = 2024.01.03 and SecurityID = `600000`

// 多个分区
select * from t
where TradeDate between 2024.01.03 and 2024.01.05
  and SecurityID in [`600000`, `600036`]
```

## 分区剪枝（**最重要**）

WHERE 必须用分区列 + DDB 能识别的写法，否则全表扫。

### ✅ 触发剪枝的写法

```dolphindb
where TradeDate = 2024.01.03
where TradeDate between 2024.01.03 and 2024.01.05
where TradeDate >= 2024.01.01 and TradeDate <= 2024.01.05
where TradeDate in [2024.01.03, 2024.01.04]
where SecurityID = `600000`        // HASH 分区列也可剪枝
```

### ❌ 不触发剪枝（全表扫）

```dolphindb
where 2024.01.01 <= TradeDate <= 2024.01.05    // 链式比较
where year(TradeDate) = 2024                    // 分区列被函数包裹
where temporalAdd(TradeDate,1,'d') > 2024.01.03 // 同上
where TradeDate + 1 = 2024.01.04                // 列上做了运算
```

### 验证剪枝

```dolphindb
// 加 [HINT_EXPLAIN] 看执行计划
select [HINT_EXPLAIN] *
from t
where TradeDate between 2024.01.03 and 2024.01.05
```

输出 `partitions.local` 的数量应该等于范围内分区数，不是全库分区数。

**实测对比**（同一查询、同一表）：

| 写法 | 扫描分区数 |
|---|---|
| `where 2022.12.01 <= TradeDate <= 2022.12.03` | 10091（全表扫） |
| `where TradeDate between 2022.12.01 and 2022.12.03` | 90（剪枝成功） |
| `where TradeDate >= 2022.12.01 and TradeDate <= 2022.12.03` | 90 |

## INSERT / 写入

```dolphindb
// 方式 1：tableInsert（推荐，可链式）
t1 = loadTable(dbName, tbName)
rows = t1.tableInsert(newData)

// 方式 2：append!
loadTable(dbName, tbName).append!(newData)

// 方式 3：insert into（只能逐行小批）
insert into snapshot values(2024.01.03, 09:30:00.000, `600000`, 10.5, ...)

// 方式 4：upsert!（按 key 去重写入）
loadTable(dbName, tbName).upsert!(
    newData,
    keyColNames=[`TradeDate, `TradeTime, `SecurityID]
)
```

**append! 列对齐警告**：DDB 不检查列名，**只按位置**。如果列顺序错位，数据全错且不报错。导入前必做：

```dolphindb
expectedCols = loadTable(dbName, tbName).schema().colDefs.name
newData.reorderColumns!(expectedCols)   // 强制对齐
```

## DELETE

### 按分区删（**首选**）

```dolphindb
db = database(dbName)
dropPartition(db, [2024.01.03], tableName=tbName)              // 单天
dropPartition(db, [2024.01.03..2024.01.05], tableName=tbName)  // 多天
```

秒级，不占内存。

### 按条件删（慢）

```dolphindb
delete from loadTable(dbName, tbName) where SecurityID = `600000`
```

会扫描所有分区，**OLAP 引擎不支持**，只能用 `dropPartition`。

### 清空整张表

```dolphindb
truncate(dbName, tbName)              // 保留表结构
dropTable(db, tbName)                 // 表结构也删
dropDatabase(dbName)                  // 整个库
```

## UPDATE

```dolphindb
update loadTable(dbName, tbName)
set ask1 = OfferPrice[0], bid1 = BidPrice[0]
where TradeDate = 2024.01.03
```

**OLAP 不支持 UPDATE**，TSDB 才行。OLAP 要改数据：删分区 → 重写。

## 函数式 SQL（动态构造）

适合脚本里按参数拼条件，比拼字符串更安全：

```dolphindb
dt = 2024.01.03
sid = `600000

// sql() 构造，再用 sqlDS / executeSQL 跑
q = sql(
    select = sqlCol(`LastPrice).avg(),
    from = loadTable(dbName, tbName),
    where = expr(sqlCol(`TradeDate), ==, dt)
)
// 跑：把 q 喂给 mr / 或直接拿 SQL 文本
print(q)                  // 看生成的 SQL
```

**meta SQL 慎用**：能写死的就不要动态拼，可读性和性能都更好。

## 大结果集分页拉取

服务端 SELECT 结果太大 → 客户端 OOM。Python SDK 用 `fetchSize`：

```python
block = s.run("select * from loadTable('dfs://x','t') where TradeDate=2024.01.03",
              fetchSize=8192)
while block.hasNext():
    chunk = block.read()           // pd.DataFrame
    process(chunk)
# block.skipAll()                  // 不需要剩余数据时调
```

或者**先在服务端聚合再拉**：

```python
# ❌ 拉 1 亿行下来再 groupby
df = s.run("select * from loadTable(...) where TradeDate=2024.01.03")
df.groupby('SecurityID')['LastPrice'].mean()

# ✅ 服务端 group by，只拉结果
df = s.run("select avg(LastPrice) from loadTable(...) where TradeDate=2024.01.03 group by SecurityID")
```

## 查询优化必修

### 1. 聚合查询合并成一次

```python
# ❌ 3 次往返
min_d = s.run("select min(TradeDate) from loadTable('dfs://x','t')")
max_d = s.run("select max(TradeDate) from loadTable('dfs://x','t')")
cnt   = s.run("select count(*) from loadTable('dfs://x','t')")

# ✅ 1 次
r = s.run("""
    select min(TradeDate) as earliest, max(TradeDate) as latest, count(*) as total
    from loadTable('dfs://x','t')
""")
```

### 2. 只 select 需要的列

```dolphindb
// ❌ 30 列全传
select * from loadTable('dfs://x','t') where TradeDate=2024.01.03

// ✅ 只取要的
select TradeDate, TradeTime, SecurityID, LastPrice, TotalVolumeTrade
from loadTable('dfs://x','t') where TradeDate=2024.01.03
```

列式存储，少列就少 IO。

### 3. 多因子查询用 pivot by（服务端转列）

```dolphindb
// ❌ Python 端 merge：N 个因子 N 次查询 + N 次 join
// ✅ 服务端一次 pivot 完成宽表
select value from loadTable('dfs://factor','f')
where TradeDate between 2024.01.01 and 2024.01.31
pivot by TradeDate, SecurityID, factorName
```

### 4. 分页语法（**DDB ≠ 标准 SQL**）

```dolphindb
// ❌ 标准 SQL OFFSET 关键字 DDB 不支持
select * from loadTable('dfs://x','t') limit 100 offset 200

// ✅ DDB 分页语法：limit 跳过行数, 返回行数
select * from loadTable('dfs://x','t') limit 200, 100
//                                            ^^^  ^^^
//                                          offset count
```

## 常用聚合

```dolphindb
// 行级
select first(LastPrice), last(LastPrice), max(HighPrice), min(LowPrice),
       avg(LastPrice), sum(TotalVolumeTrade), count(*), wavg(LastPrice, TotalVolumeTrade)
from t where TradeDate=2024.01.03 group by SecurityID

// 分桶（5 分钟 K 线）
select first(LastPrice) as open, max(HighPrice) as high,
       min(LowPrice) as low, last(LastPrice) as close,
       sum(TotalVolumeTrade) as vol
from t
where TradeDate=2024.01.03
group by SecurityID, bar(TradeTime, 5*60*1000) as bar5min

// interval 填充缺失桶
select last(LastPrice) as close
from t
group by SecurityID, interval(X=TradeTime, duration=60s, label='left', fill=0) as bar1min
```

## context by 与 csort（**分组内排序**）

`group by` 聚合后只剩一行，`context by` 保留所有行（窗口运算）：

```dolphindb
// 按股票分组、按时间排序，算每只股的累计成交量
select TradeDate, TradeTime, SecurityID, TotalVolumeTrade,
       cumsum(TotalVolumeTrade) as cumVol
from t where TradeDate=2024.01.03
context by SecurityID csort TradeTime
```

`csort` 默认升序。`csort TradeTime desc` 降序。

## pivot（行列转换）

```dolphindb
// 输出矩阵：行 = 时间，列 = 股票
m = exec last(LastPrice) from t
    where TradeDate=2024.01.03
    pivot by TradeTime, SecurityID

// 截面排名
rowRank(m)
```

`exec` 是 `select` 的标量版本，配合 `pivot by` 出矩阵。

跨引用：批计算 → [[sql-batch-compute]]，慢查询排查 → [[performance-tuning]]。
