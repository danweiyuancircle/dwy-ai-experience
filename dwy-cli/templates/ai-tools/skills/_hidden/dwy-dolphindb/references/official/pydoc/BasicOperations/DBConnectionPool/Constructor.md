---
source_url: https://docs.dolphindb.cn/zh/pydoc/BasicOperations/DBConnectionPool/Constructor.html
fetched_at: 2026-05-19T09:52:40Z
category: pydoc
title: DBConnectionPool
sha1: 419a1f8263aa8bff497aad5ff0a0e778a6096866
---

# DBConnectionPool

DBConnectionPool （连接池）可以实现并发执行脚本。由前一章节的内容可知，session（会话控制）可以实现 API 客户端与 DolphinDB 之间的信息交互。Python API 通过 session 在 DolphinDB 上执行脚本和函数，同时实现双向的数据传递。但由于 session 只能调用 `run()` 方法来串行执行脚本，且无法在多线程中使用同一 session 执行脚本。因此，若需要并发地执行脚本，建议使用 DBConnectionPool 以提高任务运行的效率。

DBConnectionPool 通过创建多个线程以实现并发执行任务。如下展示创建一个 DBConnectionPool 的完整示例：

```dolphindb
DBConnectionPool(host, port, threadNum=10, userid=None, password=None, 
                 loadBalance=False, highAvailability=False, compress=False,  
                 reConnect=False, python=False, protocol=PROTOCOL_DEFAULT,
                 *,
                 show_output=True, sqlStd=SqlStd.DolphinDB, tryReconnectNums=None, parser= ParserType.Default, usePublicName=False)
```

通过调用方法函数 `getSessionId()` 来获取 DBConnectionPool 对象创建的所有线程会话的 session id。若不再使用当前 DBConnectionPool，API 会在析构时自动释放连接。

以下内容将对创建 DBConnectionPool 的相关参数进行详细说明。

## 连接参数 *host*, *port*, *threadNum*, *userid*, *password*, *usePublicName*

- **host** ：所连接服务器的地址。
- **port** ：所连接服务器的端口。
- **threadNum** ：建立连接的数量，默认为10。
- **userid** ：登录时的用户名。
- **password** ：登录时用户名对应的密码。
- **usePublicName**：布尔值，可选，默认值为 False。指定在在集群环境下是否使用节点的 publicName 作为连接地址。若设置为 True，需要 DolphinDB server 配置 publicName。

用户可以使用指定的域名（或 IP 地址）和端口号把 DBConnectionPool 连接到 DolphinDB，并且在建立连接的同时登录账号。使用示例如下：

```dolphindb
import dolphindb as ddb

# 连接地址为localhost，端口为8848的DolphinDB，连接数为10
pool = ddb.DBConnectionPool("localhost", 8848)

# 连接地址为localhost，端口为8848的DolphinDB，登录用户名为admin，密码为123456的账户，连接数为8
pool = ddb.DBConnectionPool("localhost", 8848, 8, "admin", "123456")
```

**注意**：

- 在构造 DBConnectionPool 时，必须指定参数 *host*, *port*。

## 负载均衡参数 *loadBalance*

- **loadBalance**：连接池负载均衡相关配置参数，默认值为 False。

该参数的默认值为 False，表示不开启负载均衡。若要开启负载均衡，则将参数设置为 True。示例脚本如下：

```dolphindb
import dolphindb as ddb

# 创建连接池；开启负载均衡
pool = ddb.DBConnectionPool("localhost", 8848, 8, loadBalance=True)
```

**注意，在负载均衡模式下：**

- 如果开启高可用，则可连接节点为集群中所有数据节点。此时负载均衡参数无效。
- 如果不开启高可用模式，则 DBConnectionPool 会向所有可连接的数据节点均匀建立连接。例如，集群中有 3 个节点，当前连接数分别为[5, 12, 13]，DBConnectionPool 的连接数为 6，则在建立连接后，集群中 3 个节点的连接数分别为[7, 14, 15]，即每个节点均增加 2 个连接数。

## 高可用参数 *highAvailability*

- **highAvailability** ：是否在集群所有节点上进行高可用配置，默认值为 False。

在高可用模式下，如果不启用负载均衡模式，DBConnectionPool 会和当前集群中负载最小的节点建立连接。但由于 DBConnectionPool 中的连接为同时建立，每个连接计算出的负载值几乎一致，导致所有连接会和同一个节点建立连接，故无法保证节点资源的负载均衡。

示例脚本如下：

```dolphindb
import dolphindb as ddb

# 创建连接池；开启高可用，使用集群所有节点作为高可用节点
pool = ddb.DBConnectionPool("localhost", 8848, 8, "admin", "123456", highAvailability=True)
```

## 压缩参数 *compress*

- **compress**：当前连接是否开启压缩，默认参数为 False。

该模式适用于大数据量的写入或查询。压缩数据后再传输，这可以节省网络带宽，但会增加 DolphinDB 和 API 端的计算量。使用示例如下：

```dolphindb
import dolphindb as ddb
import dolphindb.settings as keys

# api version >= 1.30.21.1，开启压缩，需指定协议为PROTOCOL_DDB
pool = ddb.DBConnectionPool("localhost", 8848, 8, compress=True, protocol=keys.PROTOCOL_DDB)

# api version <= 1.30.19.4，开启压缩，默认使用协议为PROTOCOL_DDB，即enablePickle=False
pool = ddb.DBConnectionPool("localhost", 8848, 8, compress=True)
```

**注意**：

- DolphinDB 自1.30.6版本起支持压缩参数 *compress*。
- 目前仅在配置协议参数 *protocol* 为 PROTOCOL\_DDB 的情况下支持开启压缩。（API version<=1.30.19.4 时，默认协议使用PROTOCOL\_DDB，支持开启压缩）

## 重连参数 *reConnect*, *tryReconnectNums*

- **reConnect**：bool 类型，默认值为 False。在不开启高可用的情况下，是否在 API 检测到连接异常时进行重连。
- **tryReconnectNums**：int 类型，表示重连尝试次数。
  - 若不开启高可用，须与 *reconnect* 参数搭配使用，对单节点进行有限次重连。若不填写该参数，默认进行无限重连。
  - 当开启 *highAvailability* 高可用参数时，
    - 若指定该参数，将在断开连接后遍历可用节点列表内的每个节点进行有限次重连。一次遍历中，每个节点只会被重连一次，最多进行 *tryReconnectNums* 次遍历尝试。
    - 若不填写该参数，默认是无限重连。

若开启高可用模式，则 API 在检测到连接异常时将自动进行重连，不需要设置参数 *reConnect*。若未开启高可用，通过配置 `reConnect = True`，即可实现 API 在检测到连接异常时进行重连。使用示例如下：

```dolphindb
import dolphindb as ddb

# 创建连接池；开启重连
pool = ddb.DBConnectionPool("localhost", 8848, 8, reConnect=True, tryReconnectNums=5)
```

## 协议参数 *protocol*

- **protocol**：API 与 DolphinDB 交互时使用的数据格式协议，默认值为 PROTOCOL\_DEFAULT，表示使用 PROTOCOL\_DDB。注：3.0.1.1 及之前版本，protocol 默认使用 PROTOCOL\_PICKLE。

目前 DolphinDB 支持三种协议：PROTOCOL\_DDB, PROTOCOL\_PICKLE, PROTOCOL\_ARROW。使用不同的协议，会影响 API 执行 DolphinDB 脚本后接收到的数据格式。有关协议的详细说明请参考章节[类型转换](../../AdvancedOperations/DataTypeCasting/TypeCasting.html)。

```dolphindb
import dolphindb.settings as keys

# 使用协议 PROTOCOL_DDB
pool = ddb.DBConnectionPool("localhost", 8848, 10, protocol=keys.PROTOCOL_DDB)

# 使用协议 PROTOCOL_PICKLE
pool = ddb.DBConnectionPool("localhost", 8848, 10, protocol=keys.PROTOCOL_PICKLE)

# 使用协议 PROTOCOL_ARROW
pool = ddb.DBConnectionPool("localhost", 8848, 10, protocol=keys.PROTOCOL_ARROW)
```

**注意 1**：在 1.30.21.1 版本及之后，API 支持使用 *protocol* 来指定数据格式协议。1.30.19.4 版本及之前，默认 API 内部使用 PROTOCOL\_DDB，即 `enablePickle=False`。

**注意 2**：自 Python API 3.0.3.0 起，针对 Python 3.13 及以上版本的安装包将不再支持 PICKLE 协议。

## 其他参数 *show\_output*

- **show\_output**：是否在执行后打印脚本中 print 语句的输出。默认值为 True，表示打印 print 语句输出。

使用示例如下：

```dolphindb
# 启用 show_output
pool = ddb.DBConnectionPool("localhost", 8848, 8, show_output=True)
taskid = 12
pool.addTask("print(1);2", taskId=taskid)
while True:
    if pool.isFinished(taskId=taskid):
        break
    time.sleep(0.01)

res = pool.getData(taskId=taskid)
print(res)

// output:
1
2

# 不启用 show_output
pool = ddb.DBConnectionPool("localhost", 8848, 8, show_output=False)
taskid = 12
pool.addTask("print(1);2", taskId=taskid)
while True:
    if pool.isFinished(taskId=taskid):
        break
    time.sleep(0.01)

res = pool.getData(taskId=taskid)
print(res)

// output:
2
```

## SQL 方言参数 *sqlStd*

- **sqlStd** ：执行脚本时采用的 SQL 方言标准。现支持三种方言：DolphinDB（默认值），Oracle 和 MySQL。

注：DolphinDB 服务端自 2.00.10、1.30.22 起开始支持 Oracle 和 MySQL 方言。Python AIP 自 3.0.2.0 版本起开始支持该参数， 方便用户选择方言。

在使用时，需要从 dolphindb.settings 中引入 SqlStd，并通过 SqlStd 枚举类型来指定该参数。

```dolphindb
import dolphindb as ddb
from dolphindb.settings import SqlStd

pool = ddb.DBConnectionPool("localhost", 8848, 10, sqlStd=SqlStd.Oracle)
```

## 解析器参数 *python*, *parser*

- **python**：布尔值，默认值为 False。是否启用 python parser 特性（在 Python API 3.0.3.0 中弃用）。
- **parser**：字符串标量，用于指定脚本解析器。可选值有 "dolphindb", "python", "kdb"。默认为 "dolphindb"。推荐使用 *parser* 参数指定解析器类型。

指定 *parser* 参数后，可以在 `DBConnectionPool.run` 执行脚本时选择脚本解析器。使用示例如下：

```dolphindb
import dolphindb as ddb

# 启用 python parser
pool = ddb.DBConnectionPool("localhost", 8848, 10, parser="python")

# 启用 kdb parser
pool = ddb.DBConnectionPool("localhost", 8848, 10, parser="kdb")
```

**注意**： 仅 DolphinDB 3.00 版本支持解析器参数。
