---
topic: data-ingest
source_files:
  - official/db_distr_comp/db_oper/data_import_method.md
  - official/funcs/l/loadTextEx.md
  - official/funcs/l/loadText.md
  - official/funcs/t/textChunkDS.md
  - official/pydoc/BasicOperations/table_append.md
---

# 数据导入

DolphinDB 数据导入选型与高性能落库指南。覆盖 CSV / Parquet / Python DataFrame / MySQL / Kafka / HDF5 六大数据源。

## 30 秒导入选型

| 数据源 | 推荐方式 | 关键函数 / 接口 | 适用场景 |
|---|---|---|---|
| CSV 小文件（< 1GB） | 单次落库 | `loadTextEx` | 一次性导入，直接落 DFS 表 |
| CSV 大文件（> 1GB） | 切片 + map-reduce | `textChunkDS` + `mr` | 内存有限、需多线程并行 |
| CSV 海量小文件 | 批量合并 | `loadText` + `unionAll` + `append!` | 单文件小、数量多（如一股票一文件） |
| CSV 内存表 | 单/多线程读 | `loadText` / `ploadText` | 仅做内存分析，不落库；`ploadText` 适合 16MB+ |
| Parquet | parquet 插件 | `parquet::loadParquet` | 跨平台列式数据 |
| HDF5 | hdf5 插件 | `hdf5::loadHDF5` | 科研数据、量化历史行情 |
| Python DataFrame | API + appender | `PartitionedTableAppender` / `tableAppender` | Python 端批量写入 |
| MySQL | mysql / odbc 插件 | `mysql::load` / `odbc::query` | 关系型库迁移 |
| Kafka | kafka 插件 | `kafka::subscribe` → 流表 | 实时行情、日志 |
| 二进制 | 内置函数 | `loadRecord` / `readRecord!` | 自定义二进制协议 |
| JSON | 内置函数 | `fromJson` / `fromStdJson` | 配置、嵌套对象 |

## 大文件导入 4 步流程

1. **估行数 / 抽样**：`wc -l file.csv`；`extractTextSchema(path)` 推断列类型
2. **切片**：`textChunkDS(file, chunkSize)`，chunkSize 取 256 ~ 1024 MB（参数范围 1 ~ 2048 MB）
3. **多线程入库**：`mr(ds, append!{pt}, , , parallel=false)` — **同分区禁并发写**
4. **批量上限**：单次 append / appender 不超过 **50 万行（500K）**，超过需切 batch

```dolphindb
ds = textChunkDS("/data/trades.csv", 500)   // 500 MB/块
mr(ds, append!{pt}, , , false)              // parallel=false 必填
```

## loadTextEx 关键参数

```
loadTextEx(dbHandle, tableName, partitionColumns, filename,
           [delimiter], [schema], [skipRows], [transform],
           [sortColumns], [atomic], [arrayDelimiter], [containHeader], [arrayMarker])
```

| 参数 | 作用 | 常见用法 |
|---|---|---|
| `schema` | 列名 / 类型 / 时间 format / 列下标 col | `extractTextSchema(path)` 再 `update` 改 type / format |
| `delimiter` | 列分隔符（默认 `,`） | TSV 用 `\t`，可多字符 |
| `partitionColumns` | 分区列 | 必填；组合分区传向量 `` `date`ID `` |
| `sortColumns` | 分区内排序列（仅 TSDB） | 高频查询字段靠前；最后一列须时间 / 整型；每分区 sort key ≤ 2000 |
| `transform` | 入库前一元函数 | `nullFill!{,0}` 填空、`mytrans{,sym}` 加列 / 调列序 |
| `skipRows` | 跳过文件头行数 | 0 ~ 1024 |
| `atomic` | 单文件是否原子事务 | 文件 > Cache Engine 必须 `false`，否则事务卡死 |
| `containHeader` | 是否含标题行 | 默认自动判断 |
| `arrayDelimiter` | 数组向量分隔符 | 配合 `schema.type = "DOUBLE[]"` 使用 |
| `encoding` | 源文件编码 | **必须 UTF-8**；GBK 须先转码 |

注：列名非中英文/数字/下划线会被自动改写（如 `1_test` → `c1_test`，`test-a!` → `test_a_`）。

## 写入性能基线

| 写入方式 | 吞吐量级 | 适用 | 备注 |
|---|---|---|---|
| `loadTextEx` (CSV → DFS) | 100 ~ 300 万行/秒 | 离线全量入库 | 单线程，分批落盘，内存占用低 |
| `textChunkDS` + `mr` | 200 ~ 500 万行/秒 | 大文件多线程 | `parallel=false`，靠多分区并行 |
| `PartitionedTableAppender` (Python) | 100 ~ 200 万行/秒 | Python 批量回填 | 连接池 + 分区路由，最高效 |
| `tableAppender` (Python) | 50 ~ 100 万行/秒 | Python 单连接追加 | 一般小数据量 / 流式追加 |
| `tableInsert` / `append!` | 50 ~ 100 万行/秒 | 实时流写入 | 单次建议 1 ~ 50 万行 |
| 单行 `insert into` | < 1 万行/秒 | 调试 | 生产禁用 |

## 典型导入 3 例

### 例 1. loadTextEx：CSV → DFS（含 transform 加列 + sortColumns）

```dolphindb
db = database("dfs://stock_data", VALUE, 2000.01M..2025.12M, , "TSDB")
schema = extractTextSchema("/data/sz000001.csv")
update schema set type="DATETIME" where name="tradetime"

def mytrans(mutable t, sym, colNames) {
    t1 = select sym, * from t
    t1.reorderColumns!(colNames)
    return t1
}
loadTextEx(db, `pt, `tradetime, "/data/sz000001.csv",
           schema=schema,
           transform=mytrans{,"sz000001", colNames},
           sortColumns=`sym`tradetime)
```

### 例 2. textChunkDS + mr：3GB 大文件多线程

```dolphindb
db = database("dfs://db1", VALUE, `IBM`MSFT`GOOG`AMZN`TSLA)
pt = db.createPartitionedTable(trades, `pt, `sym)
ds = textChunkDS("/data/trades.txt", 500)   // 500MB/块
mr(ds, append!{pt}, , , false)              // parallel 必为 false
```

### 例 3. Python pool + PartitionedTableAppender

```python
import dolphindb as ddb
pool = ddb.DBConnectionPool("localhost", 8848, 8, "admin", "123456")
appender = ddb.PartitionedTableAppender(
    dbPath="dfs://stock", tableName="pt",
    partitionColName="date", dbConnectionPool=pool)
# uint 列须先转换；NaN 自动转 NULL
df["qty"] = df["qty"].astype("int64")
appender.append(df)   # 单批 ≤ 500K 行
```

## 常见陷阱

| 陷阱 | 表现 | 解决 |
|---|---|---|
| 单批超 50 万行 | append 卡顿 / OOM | 切分 batch，单次 ≤ 500K |
| 文件 GBK 编码 | 中文乱码 | 先 `iconv -f GBK -t UTF-8` 转码 |
| `mr` 用 `parallel=true` | 同分区并发写抛异常 | 必须 `parallel=false` |
| DataFrame 含 uint | API 写入类型不匹配 | `.astype("int64")` 显式转换 |
| DataFrame 含 NaN | 期望写 NULL | 数值列自动转；object 列须 `.where(pd.notna(df), None)` |
| `loadText` 单线程慢 | 16MB+ 文件耗时 | 改用 `ploadText` 多核并行 |
| 时间列被识别为 LONG | 形如 `20190623145457` | schema 指定 `type=DATETIME` + `format="yyyyMMddHHmmss"` |
| `atomic=true` + 大文件 | 事务卡死（既不能 commit 也不能 rollback） | 文件超 Cache Engine 必须 `atomic=false` |
| 数组向量列识别失败 | 默认按字符串读 | schema 改 `type="DOUBLE[]"` + `arrayDelimiter` |
| 海量小文件逐个导 | 效率极低 | 批量 `each(loadText, files).unionAll(false)` 后 append |
| schema 自动推断错列类型 | 抽样不准 | 显式传 `schema`，类型 / format 强制指定 |
| 列名以数字开头 | 被改名为 `c1_xxx` | 数据文件预处理或接受自动改名 |

## 下钻原文

- 导入方法总览：`../official/db_distr_comp/db_oper/data_import_method.md`
- loadTextEx 全参 / transform / sortColumns 示例：`../official/funcs/l/loadTextEx.md`
- loadText / schema / arrayMarker / 批量小文件：`../official/funcs/l/loadText.md`
- textChunkDS + mr 大文件切片：`../official/funcs/t/textChunkDS.md`
- Python API 追加（tableAppender / PartitionedTableAppender）：`../official/pydoc/BasicOperations/table_append.md`
