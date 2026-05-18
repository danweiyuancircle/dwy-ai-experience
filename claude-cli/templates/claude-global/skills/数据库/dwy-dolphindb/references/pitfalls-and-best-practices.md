# 反模式与最佳实践

## 类型陷阱

### 1. DATETIME 2038 溢出

```dolphindb
// ❌ 32 位 int，范围 [1901.12.13T20:45:53, 2038.01.19T03:14:07]
//    超出 → 整数溢出 → 显示 1970 异常
t = table(1:0, `ts, [DATETIME])

// ✅ 全用 TIMESTAMP（毫秒精度，64 位 long）
t = table(1:0, `ts, [TIMESTAMP])
```

**铁律**：新表别用 `DATETIME`，统一 `TIMESTAMP`。

### 2. FLOAT/DOUBLE 精度（金融场景禁用）

```dolphindb
0.1 + 0.2 == 0.3                 // false! (DOUBLE 精度问题)
eqFloat(0.1 + 0.2, 0.3)          // true（专用比较函数）

// ❌ 价格用 DOUBLE
price DOUBLE

// ✅ 用 DECIMAL
price DECIMAL64(6)               // 6 位小数，精确到 0.000001
```

DECIMAL 比 DOUBLE 慢 ~30%，但金融场景必须用。

### 3. CHAR 不自动转 SYMBOL

```dolphindb
// ❌ CHAR 直接 append 到 SYMBOL 列
c = char(65)                     // 'A'
symbolVec.append!(c)             // 报错或乱码

// ✅ 显式转 STRING
symbolVec.append!(c.string())    // STRING 会自动转 SYMBOL
```

### 4. 除法运算 `/` 和 `\` 反过来

```dolphindb
100 / 3                          // 33（取整）
100 \ 3                          // 33.333333...（浮点）
```

DDB 和 Python/SQL **相反**！老手都踩过。要小数结果用 `\`。

### 5. SYMBOL ≤255 字节 / STRING 64KB / BLOB 64MB 静默截断（**1.30.23 / 2.00.11 起**）

| 类型 | 上限 | 超限行为 |
|---|---|---|
| `SYMBOL` | **≤ 255 字节** | **整批 append 直接抛异常**，写入失败 |
| `STRING` | < 64 KB | 静默截断到 65535 字节 |
| `BLOB` | < 64 MB | 静默截断到 67108863 字节 |

**SYMBOL 校验是写入前必做**，否则整批失败：

```python
MAX_SYMBOL_BYTES = 255

# UTF-8 字节数 = .encode() 后长度（中文 1 字 ≈ 3 字节）
oversize = batch_df["order_book_id"].str.encode("utf-8").str.len() > MAX_SYMBOL_BYTES
if oversize.any():
    raise ValueError(f"SYMBOL 列有 {oversize.sum()} 行超过 255 字节")
```

**STRING/BLOB 截断不可逆**：写入前必须做长度断言，事后无法恢复原数据。

类型选择：
- 短编码（股票代码、因子名）→ `SYMBOL`，但校验 ≤255 字节
- 中等文本（备注、描述）→ `STRING`，应用层卡 64KB
- 大文本/二进制（JSON、文件）→ `BLOB`，应用层卡 64MB

### 6. NULL / NaN / 空字符串 区别

| 值 | 类型 | 表达 |
|---|---|---|
| NULL | VOID / 类型化 | `NULL`, `int()`, `00i` |
| NaN | FLOAT/DOUBLE | 无效数值结果 |
| 空字符串 | STRING | `""` |

```dolphindb
isNull(NULL)                     // true
isNull(NaN)                      // true
isNull("")                       // false! 空串不是 NULL
```

填空用：`nullFill(x, 0)`、`ffill(x)`（前值填充）。

## DDB 脚本语法陷阱

### 1. backtick 列名必须单行

```dolphindb
// ❌ 多行 backtick 列名 → 语法错误
schema = table(1:0,
    `col1`col2
    `col3`col4,
    [INT, INT, INT, INT])

// ✅ 单行定义；多列必须先变量化
colNames = `col1`col2`col3`col4
colTypes = [INT, INT, INT, INT]
schema = table(1:0, colNames, colTypes)
```

### 2. 多值 SYMBOL 拼接

```python
# ✅ DDB 语法：`v1`v2`v3 是 SYMBOL 向量字面量
symbols = ["000001.XSHE", "000002.XSHE"]
symbols_str = "`" + "`".join(symbols)
script = f"... where order_book_id in [{symbols_str}]"
# 生成：where order_book_id in [`000001.XSHE`000002.XSHE]
```

### 3. 脚本拼接用 `;\n` 分隔

```python
# ✅ 多语句之间必须分号 + 换行
script = (
    f'tickData = select * from loadTable("dfs://x","t") where {flt};\n'
    f'{user_script};\n'
    f'exec count(*) from result'
)
```

## SQL 陷阱

### 1. append! 不检查列名

```dolphindb
// 目标表：t(a INT, b DOUBLE)
src = table(1.5 as b, 1 as a)
t.append!(src)                   // 不报错，但 a 列拿到 1.5（被截断为 1），b 拿到 1.0
```

**铁律**：append 前必须 `reorderColumns!`：
```dolphindb
src.reorderColumns!(t.schema().colDefs.name)
t.append!(src)
```

### 2. WHERE 包裹分区列函数 → 不剪枝

```dolphindb
// ❌ 函数包裹了分区列
where year(TradeDate) = 2024
where temporalAdd(TradeDate, 1, 'd') > 2024.01.03

// ✅ 直接比较
where TradeDate >= 2024.01.01 and TradeDate < 2025.01.01
```

### 3. 不触发分区剪枝的 WHERE（**慢查询头号原因**）

```dolphindb
// ❌ 链式比较 DDB 不识别
where 2024.01.01 <= TradeDate <= 2024.01.05

// ❌ 列被函数包裹
where year(TradeDate) = 2024
where temporalAdd(TradeDate, 1, 'd') > 2024.01.03

// ❌ 列上做运算
where TradeDate + 1 = 2024.01.04

// ✅ 全部改成直接比较 / between / in
where TradeDate between 2024.01.01 and 2024.01.05
where TradeDate >= 2024.01.01 and TradeDate <= 2024.01.05
where TradeDate in [2024.01.03, 2024.01.04]
```

**验证是否剪枝**：`select [HINT_EXPLAIN] * from t where ...`，看输出的 `PartitionInfo` 扫描数。详见 [[crud-operations]] 「分区剪枝」一节。

### 4. group by 必须搭配聚合

```dolphindb
// ❌ select 含非聚合列且不在 group by 里
select TradeTime, SecurityID, sum(vol) from t group by SecurityID

// ✅
select SecurityID, sum(vol) from t group by SecurityID
// 或保留所有行用 context by
select TradeTime, SecurityID, sum(vol) from t context by SecurityID
```

### 5. select 出来一定是表

```dolphindb
// 想要标量
x = select avg(price) from t   // 这是只有 1 行 1 列的 table，不是数字

// 取标量
x = exec avg(price) from t     // exec 才返回标量/向量
```

## 库表设计反模式

### 1. TSDB sortColumns 用唯一列

```dolphindb
// ❌ orderId 是唯一的 → 索引膨胀
sortColumns = ["orderId"]

// ✅ 业务键 + 时间
sortColumns = ["SecurityID", "TradeTime"]
```

### 2. VALUE 分区预建大量空分区

```dolphindb
// ❌ 一次建 10 年空分区，元数据爆炸
partitioned by VALUE(2020.01.01..2030.12.31)

// ✅ 建初始几天，VALUE 会自动扩展
partitioned by VALUE(2024.01.01..2024.01.07)
```

### 3. 分区粒度过细

```dolphindb
// ❌ 按分钟分区，一天 240 个分区，10 天 2400 个
partitioned by VALUE(09:30:00..15:00:00)

// ✅ 日级分区已足够并行
partitioned by VALUE(2024.01.01..2024.01.07)
```

目标：单分区压缩后 **TSDB 400MB-1GB / OLAP 100MB-300MB**。

### 4. 主键、唯一索引、自增列

DDB 全部**不支持**。靠业务保证唯一性，用 `upsert!(keyColNames=...)` 做去重。

### 5. 改字段顺序、删分区列、改分区列类型

全部**不支持**。建表前用一周数据 dry-run。

## 写入反模式

### 1. 多 worker 并发写同一分区

```dolphindb
// ❌ parallel=true 写同一 DFS 表
mr(ds, tableInsert{loadTable(dbName,tb)}, parallel=true)

// ✅ 写入 mr 必须 parallel=false
mr(ds, tableInsert{loadTable(dbName,tb)}, parallel=false)
```

要并发写 → 用 `PartitionedTableAppender` 按分区列分发。

### 2. for 循环逐行 insert

```dolphindb
// ❌ 1 万行循环 = 1 万次事务
for(row in rows){
    insert into t values(row[0], row[1], row[2])
}

// ✅ 批量
t.tableInsert(rows)
```

### 3. 没显式关闭 session / pool

Python 长服务必用 try/finally 或 context manager。512 连接很快就吃满。

## 运维反模式（**会丢数据**）

### 1. 直接拷贝底层文件做迁移

❌ 不要 `cp -r /dolphindb/data /backup/`
✅ 用 `backup()` 和 `restore()` 函数

### 2. 改 hostname / IP 不停服

集群元数据里有 host 引用，改了直接起不来。必须先停集群 → 改配置 → 起。

### 3. 删 redo log / chunk meta 目录

`dfsMetaDir / chunkMetaDir / TSDBRedoLogDir / persistenceDir` 这些目录的文件**绝对不能删**，删了数据全废。

### 4. kill -9 节点

会丢未刷盘的事务。用 `stopDataNode(`name)` 或 Web 安全关机。

### 5. 磁盘 100% 后再处理

磁盘满 → 写入卡 → 元数据可能损坏。监控阈值设 80%。

## 模块/脚本管理

### 1. 改了 module 不重连

```dolphindb
clearCachedModules()             // 清缓存
use mymodule                     // 重新加载
```

否则旧版本还在 session 缓存里。

### 2. 重型脚本不用 submitJob

同步执行 = 客户端阻塞、keepAlive 超时断连。

```dolphindb
// ❌ 客户端 hang
re = mr(ds, calcHeavy, , unionAll, false)

// ✅ 异步提交，去 getRecentJobs 看进度
jobId = submitJob("calcHeavy", "monthly calc", {def(){
    re = mr(ds, calcHeavy, , unionAll, false)
    loadTable(dbName, "result").tableInsert(re)
}})
```

## 字符编码

```dolphindb
// CSV 是 GBK，DDB 默认 UTF-8 → 乱码
loadTextEx(..., schema=schema, encoding="GBK")

// 字符串编码转换
str.convertEncode("GBK", "UTF-8")
```

## Best Practice 速查

| 场景 | 做法 |
|---|---|
| 时间列 | 一律 `TIMESTAMP`（不要 DATETIME） |
| 价格金额 | `DECIMAL64(6)` 或 `DECIMAL32(3)` |
| 股票代码 | `SYMBOL` |
| 10 档行情 | 数组向量 `DOUBLE[]` 一列 |
| 单调列压缩 | `compress="delta"` |
| 删数据 | `dropPartition` 不要 `delete from` |
| 改数据 | OLAP 删分区重写，TSDB `update` 或 `upsert!` |
| 写并发 | `PartitionedTableAppender` + pool size 3 |
| 大查询 | 服务端聚合 + Python `fetchSize` |
| 重计算 | `submitJob` 异步 |
| 监控 | `getClusterPerf` + `pnodeRun(getConsoleJobs)` |
| 备份 | `backup()` / `restore()` 不要拷文件 |
| 关连接 | try/finally 或 context manager |

跨引用：建表选型 → [[create-database-table]]，调优 → [[performance-tuning]]。
