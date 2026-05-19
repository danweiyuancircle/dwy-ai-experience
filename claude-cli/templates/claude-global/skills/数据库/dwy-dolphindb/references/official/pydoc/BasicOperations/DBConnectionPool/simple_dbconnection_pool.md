---
source_url: https://docs.dolphindb.cn/zh/pydoc/BasicOperations/DBConnectionPool/simple_dbconnection_pool.html
fetched_at: 2026-05-19T09:52:40Z
category: pydoc
title: SimpleDBConnectionPool
sha1: 5a537f2ec62a37eef5c9ffcd339cc4aac6401c98
---

# SimpleDBConnectionPool

Python API 自 3.0.4.0 版本起，提供 SimpleDBConnectionPool 连接池，以此对连接进行管理和重用。

在使用时，先通过 SimpleDBConnectionPoolConfig 设置连接池的具体参数，并传入连接池的构造函数。连接池创建成功后，可以通过 acquire
方法获取一个连接进行使用。使用完毕后，可以调用 PoolEntry.release() 释放连接。连接重回连接池后属于闲置状态，之后可以再次被获取使用。

## 连接配置

Note:

Python API 3.0.4.0 起，所有配置类都基于 pydantic.BaseModel
实现。所有接收配置项的接口都支持通过关键字参数或字典传参。

### 连接对象设置 ConnectionSetting

- **enable\_ssl**：是否支持加密通讯，默认值为 False。注意：DolphinDB 须同时设置配置项 enableHTTPS=true
  方可启动 SSL 通讯。详情可参考[功能配置](https://docs.dolphindb.cn/zh/db_distr_comp/cfg/function_configuration.html#ariaid-title18)
  。
- **enable\_async**：是否支持异步通讯，默认值为 False。

  开启异步通讯后，API 端只能通过
  `Session.run()` 方法与 DolphinDB
  端进行通讯，该情况下无返回值。该模式适用于异步写入数据，可节省 API
  端检测返回值的时间。但由于执行错误也不会返回错误信息，因此通常不推荐启用。
- **compress**：是否开启压缩，默认参数为
  False。该模式适用于大数据量的写入或查询。压缩数据后再进行传输，这可以节省网络带宽，但也会增加 DolphinDB 和 API
  端的计算量。若开启压缩，必须指定 `protocol=PROTOCOL_DDB`。
- **parser**：字符串标量，用于指定脚本解析器。可选值有 "dolphindb", "python", "kdb"。默认为
  "dolphindb"。推荐使用 *parser* 参数指定解析器类型。注意： 仅 DolphinDB 3.00
  版本支持解析器参数。
- **protocol**：API 与 DolphinDB 交互时使用的数据格式协议，默认值为 PROTOCOL\_DEFAULT，表示使用
  PROTOCOL\_DDB。

  目前 DolphinDB 支持三种协议：PROTOCOL\_DDB, PROTOCOL\_PICKLE,
  PROTOCOL\_ARROW。使用不同的协议，会影响 API 执行 DolphinDB
  脚本后接收到的数据格式。有关协议的详细说明请参考章节[类型转换](../../AdvancedOperations/DataTypeCasting/TypeCasting.html)。
- **show\_output**：是否在执行后打印脚本中 print 语句的输出。默认值为 True，表示打印 print 语句输出。
- **sql\_std**：执行脚本时采用的 SQL 方言标准。现支持三种方言：DolphinDB（默认值），Oracle 和
  MySQL。

  注意：

  - DolphinDB 服务端自 2.00.10、1.30.22 起开始支持 Oracle 和 MySQL 方言。
  - 在使用时，需要从 dolphindb.settings 中引入 SqlStd，并通过 SqlStd 枚举类型来指定该参数，例如
    `sql_Std=SqlStd.DolphinDB`。

### 连接信息配置 ConnectionConfig

- **host**：所连接服务器的地址。
- **port**：所连接服务器的端口。
- **userid**：登录时的用户名。
- **password**：登录用户名对应的密码。

注意：用户可以使用指定的域名（或 IP 地址）和端口号把该会话连接到 DolphinDB，并且在建立连接的同时登录账号。

- **startup**：指定启动脚本，用于执行预加载任务。如加载插件、加载分布式表、定义并加载流数据表等。
- **enable\_high\_availability**：是否在集群所有节点上进行高可用配置，默认值为 False。
- **high\_availability\_sites**：所有可用节点的地址和端口，格式为
  `ip:port`。

*enable\_high\_availability* 和 *high\_availability\_sites* 都是 API
高可用的相关配置参数。在高可用模式下，Python API 在连接集群节点时会查询负载最小的节点，并与其建立连接。当使用单线程方式有一定延迟地创建多个
Session 时，Python API 可以保证所有可用节点上连接的负载均衡；但在使用多线程方式同时创建多个 Session
时，由于同时建立连接，集群间信息可能尚未同步，每个 Session 建立时从集群查询的最小负载节点可能为同一个，不能保证节点的负载均衡。

- **keep\_alive\_time**：在 TCP 连接状态下两次保活传输之间的持续时间，默认参数为 60，单位秒（s）。

  通过配置
  *keep\_alive\_time* 参数可以设置 TCP
  的存活检测机制的检测时长，以实现即便在网络不稳定的条件下，仍可及时释放半打开的 TCP 连接。
- **reconnect**：bool 类型，默认值为 False。在不开启高可用的情况下，是否在 API 检测到连接异常时进行重连。
- **try\_reconnect\_nums**：int 类型，表示重连尝试次数。
  - 若不开启高可用，须与 *reconnect*
    参数搭配使用，对单节点进行有限次重连。若不填写该参数，默认进行无限重连。
  - 当开启 *enable\_high\_availability* 高可用参数时，
    - 若指定该参数，将在断开连接后遍历可用节点列表内的每个节点进行有限次重连。一次遍历中，每个节点只会被重连一次，最多进行
      *try\_reconnect\_nums* 次遍历尝试。
    - 若不填写该参数，默认是无限重连。
- **read\_timeout**：int 类型，在 TCP 连接状态下的读超时时间，单位为秒（s），默认值为 None，表示无限等待。其对应
  TCP 连接的 SO\_RCVTIMEO 选项。
- **write\_timeout**：int 类型，在 TCP 连接状态下的写超时时间，单位为秒（s），默认值为 None，表示无限等待。其对应
  TCP 连接的 SO\_SNDTIMEO 选项。

通过配置超时参数，可以设置 TCP 连接的读写超时时间。例如：如果配置读超时时间为 5 秒，而执行一个需要 10
秒才能完成的脚本，则会抛出异常。写超时同理。

### 简单连接池配置 SimpleDBConnectionConfig

该配置类继承自 ConnectionSetting 和 ConnectionConfig。

**连接池大小 *min\_pool\_size, max\_pool\_size***

- **min\_pool\_size：**连接池的最小连接数，正整数，默认值为 5。初始化时，连接池会预先创建 *min\_pool\_size*
  个连接。
- **max\_pool\_size：**连接池的最大连接数，正整数，默认值为
  5。用于限制连接池中可创建的最大连接数量，防止过多连接占用数据库资源。*max\_pool\_size* 必须大于等于
  *min\_pool\_size*。

**空闲时间 *idle\_timeout***

- **idle\_timeout：**连接在连接池中允许保持空闲的最长时间，超时后将会被回收（即连接被关闭）。单位为毫秒，默认值为
  600,000（10 分钟）；最小值为 10,000（10 秒）。

**检查间隔 *check\_interval***

- **check\_interval：**后台回收线程的执行检查间隔。单位为毫秒，默认值为 60,000（1 分钟）；最小值为 1,000（ 1
  秒）。

## 相关方法

### acquire

```dolphindb
def acquire(self, timeout: int = None) -> PoolEntry: ...
```

**详情**

从连接池中获取一个可用连接对象 PoolEntry。更多信息见 [PoolEntry](#topic_i5g_2l3_mhc)。

**参数**

- **timeout：**获取连接的超时时间，单位为毫秒。如果配置该参数，超过该时间仍无法取得连接，将会报错。默认值为空，表示无限等待，直到获取到可用连接。

**返回值**

可用连接对象 `PoolEntry`。

### release

```dolphindb
def release(self, conn: PoolEntry) -> None: ...
```

**详情**

将连接对象归还至连接池。也可以通过调用 `PoolEntry.release()` 实现相同效果。

**参数**

- **conn：**
  `PoolEntry` 类型的连接对象。

### close\_idle

```dolphindb
def close_idle(self) -> None: ...
```

**详情**

清理连接池中的空闲连接，直至 total\_count（当前总连接数）降至
*min\_pool\_size*。清理时会优先回收已过期的连接。该操作为主动清理，不受自动回收策略（*idle\_timeout*）的限制。

### shutdown

```dolphindb
def shutdown(self) -> None: ...
```

**详情**

关闭连接池并清理所有相关连接。

## 相关属性

| **名称** | **类型** | **可读写性** | **含义** |
| --- | --- | --- | --- |
| active\_count | int | 只读 | 活跃连接数 |
| idle\_count | int | 只读 | 空闲连接数 |
| total\_count | int | 只读 | 总连接数 |
| is\_shutdown | bool | 只读 | 是否已手动关闭连接池 |

## 连接对象 PoolEntry

从 `SimpleDBConnectionPool` 中获取的连接对象封装为 `PoolEntry`，用于安全访问和管理池内单个连接。

### 相关方法

**run**

执行脚本/函数。接口使用方式与 `Session` 一致。

**upload**

上传变量，接口使用方式与 `Session` 一致。

**release**

```dolphindb
def release(self) -> None: ...
```

将当前连接对象归还给 `SimpleDBConnectionPool`。

注意：`PoolEntry` 支持 `with` 语法，在结束
`with` 语句时会自动将连接归还到连接池。示例请参考“使用示例”小节。

### 相关属性

| 名称 | 类型 | 可读写性 | 含义 |
| --- | --- | --- | --- |
| is\_idle | bool | 只读 | 当前是否为空闲状态。 |

## 使用示例

1. **构造
   `SimpleDBConnectionPool`**

   **方式一：**直接传入关键字参数

   ```dolphindb
   pool = ddb.SimpleDBConnectionPool(host='localhost', port=8848, min_pool_size=2, max_pool_size=5)
   ```

   **方式二：**构造
   `SimpleDBConnectionPoolConfig`
   后，传入构造函数

   ```dolphindb
   config = ddb.SimpleDBConnectionPoolConfig(host='localhost', port=8848, min_pool_size=2, max_pool_size=5)
   pool = ddb.SimpleDBConnectionPool(config=config)
   ```

   **方式三：**使用字典作为构造参数

   ```dolphindb
   pool = ddb.SimpleDBConnectionPool(config={
       'host': 'localhost',
       'port': 8848,
       'min_pool_size': 2,
       'max_pool_size': 5,
   })
   ```
2. **获取并使用连接对象 `PoolEntry`**

   **方式一：**使用
   `SimpleDBConnectionPool.acquire()` 获取连接，使用完毕后，调用
   `SimpleDBConnectionPool.release(conn)`
   归还连接。

   ```dolphindb
   conn = pool.acquire()
   print(conn.run("2 + 3"))  # Output: 5
   pool.release(conn)
   ```

   **方式二：**使用
   `SimpleDBConnectionPool.acquire()` 获取连接，使用完毕后，调用
   `PoolEntry.release()`
   归还连接。

   ```dolphindb
   conn = pool.acquire()
   print(conn.run("5 * 6"))  # Output: 30
   conn.release()
   ```

   **方式三：**使用
   `SimpleDBConnectionPool.acquire()` 获取连接，结合
   `with`
   语法可在代码块结束时自动归还连接。

   ```dolphindb
   with pool.acquire() as conn:
       print(conn.run("10.0 / 2.0"))  # Output: 5.0
   ```
