---
source_url: https://docs.dolphindb.cn/zh/pydoc/BasicOperations/Session/Constructor.html
fetched_at: 2026-05-19T09:52:40Z
category: pydoc
title: session/Session
sha1: 6bb2012d57476f2bb3d5d457b93b3779a0a7f9d6
---

# session/Session

session（会话控制）可以实现 API 客户端与 DolphinDB 服务端之间的信息交互。dolphindb 通过 session 在 DolphinDB 上执行脚本和函数，同时实现双向的数据传递。

**注意**： DolphinDB Python API 自1.30.22.1版本起调整 session 类名为 Session，同时增加别名 session 以确保兼容性。

如下展示创建一个 session 的完整示例。

```dolphindb
Session(session(host=None, port=None, userid="", password="",
        enableSSL=False, enableASYNC=False,
        keepAliveTime=30, enableChunkGranularityConfig=False, compress=False,
        enablePickle=None, protocol=PROTOCOL_DEFAULT,
        python=False, *,
        enableASYN=None, show_output=True, sqlStd=SqlStd.DolphinDB, parser= ParserType.Default,)
```

由上述脚本可知，session 的创建涉及到多个参数。以下内容将对参数进行详细说明。

## 连接参数 *host*, *port*, *userid*, *password*

- **host**：所连接服务器的地址。
- **port**：所连接服务器的端口。
- **userid** ：登录时的用户名。
- **password** ：登录时用户名对应的密码。

用户可以使用指定的域名（或 IP 地址）和端口号把该会话连接到 DolphinDB，并且在建立连接的同时登录账号。

使用示例如下：

```dolphindb
import dolphindb as ddb

# 创建 session，同时连接地址为 localhost，端口为8848的 DolphinDB
s = ddb.session("localhost", 8848)

# 创建 session，同时连接地址为localhost，端口为8848的DolphinDB，登录用户名为admin，密码为123456的账户
s = ddb.session("localhost", 8848, "admin", "123456")
```

**注意**：

- 在构造 session 时，可以不指定参数 *host*, *port*, *userid*, *password*，之后通过 connect 建立连接时再进行指定。
- 如果在构造时输入错误的参数值，将无法连接 DolphinDB，但是仍能正常创建 session 对象。

## 加密参数 *enableSSL*

- **enableSSL**：是否支持加密通讯，默认值为 False。

API 端设置脚本示例如下：

```dolphindb
# 开启加密通讯
s = ddb.session(enableSSL=True)
```

**注意**：

- DolphinDB 自 1.10.17 与 1.20.6 版本起支持加密通讯参数 *enableSSL*。
- DolphinDB 须同时设置配置项 `enableHTTPS=true` 方可启动 SSL 通讯。详情可参考[网络](https://docs.dolphindb.cn/zh/db_distr_comp/cfg/function_configuration.html#ariaid-title14)。

## 异步参数 *enableASYNC*

- **enableASYNC**：是否支持异步通讯，默认值为 False。

开启异步通讯后，API 端只能通过 `session.run()` 方法与 DolphinDB 端进行通讯，该情况下无返回值。该模式适用于异步写入数据，可节省 API 端检测返回值的时间。

使用示例如下：

```dolphindb
# 开启异步通讯
s = ddb.session(enableASYNC=True)
```

注意： Python API 自 1.20.6.0 版本起支持异步通讯参数 *enableASYN*。自 1.30.19.1 版本起，修改参数名为 *enableASYNC*。

## 保活参数 *keepAliveTime*

- **keepAliveTime**：在 TCP 连接状态下两次保活传输之间的持续时间，默认参数为 60，单位秒（s）。

使用示例如下：

```dolphindb
# 设置保活时间为120秒  
s = ddb.session(keepAliveTime=120)
```

**注意**：

- 该参数在 Linux、Windows、MacOS 平台均可生效。
- TCP 超时时间 Timeout 设置可参考 [session 相关的常用方法](OtherParams.html)。

## 压缩参数 *compress*

- **compress**：是否开启压缩，默认参数为 False。

该模式适用于大数据量的写入或查询。压缩数据后再进行传输，这可以节省网络带宽，但也会增加 DolphinDB 和 API 端的计算量。

使用示例如下：

```dolphindb
import dolphindb.settings as keys

# api version >= 1.30.21.1，开启压缩
s = ddb.session(compress=True, protocol=keys.PROTOCOL_DDB)

# api version <= 1.30.19.4，开启压缩
s = ddb.session(compress=True, enablePickle=False)
```

**注意**：

- DolphinDB 自1.30.6版本起支持压缩参数 *compress*。
- 开启压缩时，若 API 为 1.30.21.1 版本前，须指定 `enablePickle=False`；若 API 为 1.30.21.1 版本及之后，须指定协议参数 *protocol* 为 PROTOCOL\_DDB。（下一小节将介绍协议参数）

## 协议参数 *protocol*, *enablePickle*

- **protocol**：API 与 DolphinDB 交互时使用的数据格式协议，默认值为 PROTOCOL\_DEFAULT，表示使用 PROTOCOL\_DDB。注：3.0.1.1 及之前版本，protocol 默认使用 PROTOCOL\_PICKLE。
- **enablePickle**：API 与 DolphinDB 交互时是否使用 PROTOCOL\_PICKLE 作为数据格式协议，默认值为 True。

目前 DolphinDB 支持三种协议：PROTOCOL\_DDB, PROTOCOL\_PICKLE, PROTOCOL\_ARROW。使用不同的协议，会影响 API 在执行 DolphinDB 脚本后接收到的数据格式。有关协议的详细说明请参考章节[类型转换](../../AdvancedOperations/DataTypeCasting/TypeCasting.html)。

在 1.30.21.1 版本前，API 仅支持使用 *enablePickle* 来指定数据格式协议，可设置使用协议 PROTOCOL\_PICKLE, PROTOCOL\_DDB。

使用示例如下：

```dolphindb
# 使用协议 PROTOCOL_PICKLE
s = ddb.session(enablePickle=True)

# 使用协议 PROTOCOL_DDB
s = ddb.session(enablePickle=False)
```

在 1.30.21.1 版本及之后，API 支持使用 *protocol* 来指定数据格式协议，可设置使用协议 PROTOCOL\_DDB, PROTOCOL\_PICKLE, PROTOCOL\_ARROW。

使用示例如下：

```dolphindb
import dolphindb.settings as keys

# 使用协议 PROTOCOL_DDB
s = ddb.session(protocol=keys.PROTOCOL_DDB)

# 使用协议 PROTOCOL_PICKLE
s = ddb.session(protocol=keys.PROTOCOL_PICKLE)

# 使用协议 PROTOCOL_ARROW
s = ddb.session(protocol=keys.PROTOCOL_ARROW)
```

**注 1**：在设置 *protocol* 时，建议不要同时设置参数 *enablePickle*，以避免产生冲突。

**注 2**：自 Python API 3.0.3.0 起，针对 Python 3.13 及以上版本的安装包将不再支持 PICKLE 协议。

## SQL 方言参数 *sqlStd*

- **sqlStd** ：执行脚本时采用的 SQL 方言标准。现支持三种方言：DolphinDB（默认值），Oracle 和 MySQL。

注：DolphinDB 服务端自 2.00.10、1.30.22 起开始支持 Oracle 和 MySQL 方言。Python AIP 自 3.0.2.0 版本起开始支持该参数， 方便用户选择方言。

在使用时，需要从 dolphindb.settings 中引入 SqlStd，并通过 SqlStd 枚举类型来指定该参数。

```dolphindb
import dolphindb as ddb
from dolphindb.settings import SqlStd

s = ddb.Session(sqlStd=SqlStd.Oracle)
```

## 其他参数 *enableChunkGranularityConfig*

- **enableChunkGranularityConfig** ：是否支持在使用 `session.database()` 创建数据库时允许配置 *chunkGranularity* 参数，默认值为 False。

该参数会影响 `session.database()` 函数的正常使用。session 中必须指定 `enableChunkGranularityConfig=True`，否则 `session.database()` 的参数 [*chunkGranularity*](https://docs.dolphindb.cn/zh/funcs/d/database.html) 将会失效。

**注意**： 使用 *enableChunkGranularityConfig* 须在 server 的[配置文件](https://docs.dolphindb.cn/zh/db_distr_comp/cfg/function_configuration.html)中将对应参数设置为 true 时才可正常使用。

在如下脚本中，设置参数 *enableChunkGranularityConfig* 为 True，并展示参数 *chunkGranularity* 已生效：

```dolphindb
import dolphindb as ddb
import dolphindb.settings as keys

# 设置参数enableChunkGranularityConfig为True，即允许配置session.database()中的chunkGranularity参数
s = ddb.session("localhost", 8848, "admin", "123456", enableChunkGranularityConfig=True)

# 以下部分仅为展示参数chunkGranularity已生效
if s.existsDatabase("dfs://testdb"):
    s.dropDatabase("dfs://testdb")
db = s.database("db", partitionType=keys.VALUE, partitions=[1, 2, 3], dbPath="dfs://testdb", chunkGranularity="DATABASE")
print(s.run("schema(db)")["chunkGranularity"])

# 输出结果为 DATABASE
```

在如下脚本中，设置参数 *enableChunkGranularityConfig* 为 False，并展示参数 *chunkGranularity* 已失效：

```dolphindb
import dolphindb as ddb
import dolphindb.settings as keys

# 设置参数enableChunkGranularityConfig为False，即不允许配置session.database()中的chunkGranularity参数
s = ddb.session("localhost", 8848, "admin", "123456", enableChunkGranularityConfig=False)

# 以下部分仅为展示参数chunkGranularity已失效
if s.existsDatabase("dfs://testdb"):
    s.dropDatabase("dfs://testdb")
db = s.database("db", partitionType=keys.VALUE, partitions=[1, 2, 3], dbPath="dfs://testdb", chunkGranularity="TABLE")
print(s.run("schema(db)")["chunkGranularity"])

# 输出结果为 TABLE
```

## 其他参数 *show\_output*

- **show\_output**：是否在执行后打印脚本中 print 语句的输出。默认值为 True，表示打印 print 语句输出。

使用示例如下：

```dolphindb
# 启用 show_output
s = ddb.session(show_output=True)
s.connect("localhost", 8848)
s.run("print(1);2")

# 输出结果
1
2

# 不启用 show_output
s = ddb.session(show_output=False)
s.connect("localhost", 8848)
s.run("print(1);2")

# 输出结果
2
```

## 解析器参数 *python*, *parser*

- **python**：布尔值，默认值为 False。是否启用 python parser 特性（在 Python API 3.0.3.0 中弃用）。
- **parser**：字符串标量，用于指定脚本解析器。可选值有 "dolphindb", "python", "kdb"。默认为 "dolphindb"。推荐使用 *parser* 参数指定解析器类型。

使用示例如下：

```dolphindb
# 启用 python parser 特性
s = ddb.session(parser="python")

# 启用 kdb parser 特性
s = ddb.session(parser="kdb")
```

**注意**： 仅 DolphinDB 3.00 版本支持解析器参数。
