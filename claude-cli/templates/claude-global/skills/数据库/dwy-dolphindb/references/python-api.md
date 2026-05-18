# Python SDK 详解（dolphindb 3.0.4）

## 安装与版本

```bash
pip install dolphindb==3.0.4
python -c "import dolphindb as ddb; print(ddb.__version__)"
```

最低 Python 3.7+。底层 C++ via Pybind11，多线程不受 GIL。

## session.run 全用法

### 执行脚本

```python
# 单语句
s.run("x = 1")

# 多语句（用 ; 分隔，最后一句的值为返回值）
result = s.run("x=1; y=2; x+y")   # 返回 3

# 多行字符串
s.run("""
    t = table(1..10 as a, rand(100,10) as b)
    select * from t where a > 5
""")
```

### 调用 DDB 函数（参数传递）

```python
# 方式 1：所有参数在服务端
s.run("x=[1,3,5]; y=[2,4,6]")
s.run("add(x, y)")                          # array([3, 7, 11])

# 方式 2：部分应用（curry）
import numpy as np
y = np.array([1, 2, 3])
s.run("add{x,}", y)                         # 等价 add(x, y)，y 从客户端传

# 方式 3：两参数都从客户端
x = np.array([1.5, 2.5, 7])
y = np.array([8.5, 7.5, 3])
s.run("add", x, y)                          # array([10., 10., 10.])
```

### 高级参数

```python
s.run("expensiveQuery()",
    clearMemory=True,        # 跑完清理中间变量，防内存堆积
    priority=7,              # 0-9，越大越优先（默认 4）
    parallelism=2,           # 限并发，社区版 4 worker 别超 4
    fetchSize=8192,          # 大结果分段拉
    disableDecimal=False,    # True 时 DECIMAL 转 str（精度优先）
)
```

### 跑文件

```python
# test.dos 是 DDB 脚本文件
s.runFile("./scripts/calc_factor.dos")
```

## upload：Python → DDB 变量

```python
import pandas as pd

s.upload({
    'a': 8,                                  # int
    'b': "abc",                              # str
    'c': {'k1': 1, 'k2': 2},                # dict → DDB dictionary
    'arr': np.array([1, 2, 3]),             # ndarray → vector
    'df': pd.DataFrame({'x': [1,2,3]}),     # DataFrame → table
})

s.run("typestr(a)")                          # 'INT'
s.run("typestr(df)")                         # 'TABLE'
```

**注意**：upload 的变量在 session 关闭后丢失。要持久化得写进 DFS 表。

## SDK v3 异步 API（**踩坑高发**）

| 调用 | 是否 async | 用法 |
|---|---|---|
| `DBConnectionPool.run()` | ✅ **原生 async** | `await pool.run(script)` |
| `Session.run()` | ❌ 同步 | `await asyncio.to_thread(s.run, script)` |

```python
# ❌ 错：pool.run 已经是协程，再包 to_thread 会产生 "coroutine never awaited" 警告
await asyncio.to_thread(pool.run, script)

# ✅ 对：pool.run 直接 await
await pool.run(script)

# ✅ 对：Session.run 是同步的，需要 to_thread
await asyncio.to_thread(s.run, script)
```

## 数据类型映射

### Python → DolphinDB

| Python/Pandas | DolphinDB | 转换方式 |
|---|---|---|
| `int` (32 bit) | INT | — |
| `int` (64 bit) | LONG | — |
| `float` | DOUBLE | — |
| `str` | STRING | — |
| `datetime.date` | DATE | — |
| `datetime.datetime` | DATETIME / TIMESTAMP（按精度） | — |
| `numpy.ndarray` | VECTOR | — |
| `pandas.DataFrame` | TABLE | — |
| `dict` | DICTIONARY | — |
| `list of mixed` | ANY VECTOR | — |
| `uint8/16/32/64`（DDB 不接） | INT/LONG | `.astype('int64')` 显式转 |
| `float64` 含 NaN → 整数 | INT/LONG | `.fillna(0).astype('int64')` |
| `uint32`（日期如 20191205） | DATE | `pd.to_datetime(str(x), format='%Y%m%d')` |
| `uint32`（时间如 91509000） | INT | `.astype('int64')` |
| `object`（字符串） | SYMBOL | `.astype(str)` |

**硬性约束**：
- DDB **不接受 uint 类型**，所有 `uint8/16/32/64` 必须先 `.astype('int64')`，否则报错
- `NaN` **不能直接转整数**，必须先 `fillna(0)` 否则报 cast error
- `SYMBOL` 是字典编码字符串，**单值上限 255 字节**（详见 [[pitfalls-and-best-practices]] SYMBOL 长度）

### 精度差异

- pandas `datetime64[ns]` → DDB `NANOTIMESTAMP`
- pandas `datetime64[ms]` → DDB `TIMESTAMP`
- Python `Decimal` → 转 DECIMAL 时要明确 scale，否则用 `disableDecimal=True` 拿字符串

## 拉数据：DDB → Python

```python
# Table → DataFrame
table = s.loadTable(tableName='snapshot', dbPath='dfs://stock_lv2_snapshot')
df = table.toDF()

print(table.rows)            # 行数
print(table.cols)            # 列数
print(table.schema)          # schema（DataFrame 格式）

# 直接 SQL → DataFrame
df = s.run("select * from loadTable('dfs://x','t') where TradeDate=2024.01.03")
```

## 大结果分段拉取

```python
block = s.run(
    "select * from loadTable('dfs://stock_lv2_snapshot','snapshot') where TradeDate=2024.01.03",
    fetchSize=8192,
)
total = 0
while block.hasNext():
    chunk = block.read()         # pd.DataFrame
    total += len(chunk)
    process(chunk)
# 提前结束要 skipAll，否则连接阻塞
# block.skipAll()
```

## DBConnectionPool 并发

```python
import asyncio

pool = ddb.DBConnectionPool(
    "localhost", 8848,
    threadNum=3,                 # 4 worker → pool size 3
    userId="admin", password="123456",
)

async def query_one(sid):
    return await pool.run(f"""
        select avg(LastPrice) from loadTable('dfs://k','k_minute')
        where SecurityID=`{sid} and TradeDate=2024.01.03
    """)

async def main():
    sids = ['600000', '600036', '600519']
    results = await asyncio.gather(*[query_one(s) for s in sids])
    return results

results = asyncio.run(main())
pool.shutDown()
```

## 流数据订阅

```python
import dolphindb as ddb

s = ddb.session()
# 开本地接收端（必须先 enable）
s.enableStreaming(local_port=8000)    # 端口要和服务端 publish 端口区分
s.connect("localhost", 8848, "admin", "123456")

# handler：每条/每批数据回调
def on_data(msg):
    # msg 是 list（msgAsTable=False）或 DataFrame（msgAsTable=True）
    print(f"received {len(msg)} rows")
    process(msg)

# 订阅服务端流表
s.subscribe(
    host="localhost", port=8848,
    handler=on_data,
    tableName="trades_stream",       # 服务端 streamTable
    actionName="myAction",           # 订阅 ID（同表多订阅必须不同）
    offset=-1,                       # -1=最新, 0=从头, N=从第 N 条
    resub=True,                      # 断线重连
    filter=None,                     # 过滤向量
    msgAsTable=True,                 # True=每批 DataFrame, False=每条 list
    batchSize=1000,                  # 攒够 1000 条触发 handler
    throttle=1,                      # 或最多攒 1 秒
)

# 看当前订阅
print(s.getSubscriptionTopics())

# 取消
s.unsubscribe(host="localhost", port=8848,
              tableName="trades_stream", actionName="myAction")
```

**坑**：
- `enableStreaming` 的 `local_port` 不能和 DDB 服务端口冲突
- handler 抛异常**默默吃掉**，必须自己 try/except + log
- `batchSize + throttle` 是 OR 关系，先到先发

## 异步提交（不阻塞客户端）

```python
# Session 异步模式（fire-and-forget）
s.enableAsyncMode()
s.run("tableInsert{loadTable('dfs://k','k_minute')}", df)
# 立即返回，写入在服务端后台跑，**没有返回值，错误也不抛**
s.disableAsyncMode()

# 适用：高频写入，对回执不敏感
# 不适用：要确认成功、要拿结果
```

## 错误处理与重连

```python
import dolphindb as ddb
import dolphindb.settings as keys

s = ddb.session()
try:
    s.connect("localhost", 8848, "admin", "123456",
              reconnect=True, tryReconnectNums=5,
              keepAliveTime=120)
    result = s.run("select count(*) from loadTable('dfs://x','t')")
except RuntimeError as e:
    # DDB 服务端报错都是 RuntimeError
    print(f"DDB error: {e}")
    # 常见消息：
    #   "Out of memory" → 见 performance-tuning
    #   "Failed to read response" → 网络/服务端崩溃
    #   "Couldn't send script" → keepAlive 超时
finally:
    s.close()
```

## 关闭与资源回收

```python
# Session：必须显式关
s.close()

# 连接池：必须 shutDown
pool.shutDown()

# 流订阅：unsubscribe 后销毁 session
s.unsubscribe(...)
s.close()
```

**长期运行的服务**：用 context manager 包一层（DDB SDK 没原生支持，自己写）：

```python
from contextlib import contextmanager

@contextmanager
def ddb_session(host="localhost", port=8848):
    s = ddb.session()
    s.connect(host, port, "admin", "123456",
              keepAliveTime=120, reconnect=True)
    try:
        yield s
    finally:
        s.close()

with ddb_session() as s:
    df = s.run("select count(*) from loadTable('dfs://x','t')")
```

跨引用：写入对比 → [[data-import]]，性能调优 → [[performance-tuning]]，连接配置 → [[setup-and-connection]]。
