---
source_url: https://docs.dolphindb.cn/zh/pydoc/BasicOperations/Session/Connect.html
fetched_at: 2026-05-19T09:52:40Z
category: pydoc
title: Connect
sha1: 78d5044393bd3b37aeada983e8469dc9e0fdeafa
---

# Connect

dolphindb 支持以下两种创建连接的方式：

- 方式一：在构造 session 的同时传入相应参数，在构造的同时创建连接。
- 方式二：在构造 session 后，通过 connect 方法建立连接。

本节将介绍方式二，在构造 session 后通过 connect 方法建立连接。如下展示创建一个 Connect 的完整示例：

```dolphindb
connect(host, port, 
        userid=None, password=None, startup=None, 
        highAvailability=False, highAvailabilitySites=None,
        keepAliveTime=None, reconnect=False,
        *,
        tryReconnectNums=None, readTimeout=None, writeTimeout=None)
```

由上述脚本可知，使用 Connect 方法建立连接涉及到多个参数。以下内容将对参数进行详细说明。

## 连接参数 *host*, *port*, *userid*, *password*

- **host**：所连接服务器的地址。
- **port**：所连接服务器的端口。
- **userid**：登录时的用户名。
- **password**：登录时用户名对应的密码。

用户可以使用指定的域名（或 IP 地址）和端口号把该会话连接到 DolphinDB，并且在建立连接的同时登录账号。

使用示例如下：

```dolphindb
import dolphindb as ddb
s = ddb.session()

# 连接地址为localhost，端口为8848的DolphinDB
s.connect("localhost", 8848)

# 连接地址为localhost，端口为8848的DolphinDB，登录用户名为admin，密码为123456的账户
s.connect("localhost", 8848, "admin", "123456")
```

若 session 过期，或者初始化会话时没有指定登录信息（用户名与密码），可使用 `login` 方法登录 DolphinDB。

```dolphindb
import dolphindb as ddb
s = ddb.session()
# 连接地址为localhost，端口为8848的DolphinDB，未指定登录信息（用户名与密码）
s.connect("localhost", 8848)
# 使用login函数登录 DolphinDB
s.login("admin","123456")
```

## 高可用参数 *highAvailability*, *highAvailabilitySites*

- **highAvailability**：是否开启 API 高可用，默认值为 False。
- **highAvailabilitySites**：所有可用节点的地址和端口，格式为 `ip:port`。

*highAvailability* 和 *highAvailabilitySites* 都是 API 高可用的相关配置参数。在高可用模式下，Python API 在连接集群节点时会查询负载最小的节点，并与其建立连接。当使用单线程方式有一定延迟地创建多个 session 时，Python API 可以保证所有可用节点上连接的负载均衡；但在使用多线程方式同时创建多个 session 时，由于同时建立连接，每个 session 建立时查询的最小负载节点可能为同一个，不能保证节点的负载均衡。

**注意**：如果连续建立多个 session，服务端集群间可能尚未同步负载信息，此时查询到的结果可能始终为同一个最小负载节点，无法保证节点的负载均衡。

下例中为简化问题使用节点连接数代替节点负载：

1. 假如当前三个节点的负载值分别为 [1, 9, 10]，则单线程依次、有延迟地建立20个连接后，每次建立连接都会向服务器查询当前最小负载的节点，因此最后负载值分别为[14, 13, 13]。
2. 如果多线程**同时**建立 20 个连接，或单线程快速创建，则同一时刻服务器查询得到的最小负载节点为同一个，最后负载值分别为[21, 9, 10]。

节点负载的计算公式为：

```dolphindb
load = (connectionNum + workerNum + executorNum)/3.0
```

- connectionNum：连接到本地节点的连接数。
- workerNum：常规作业的工作线程的数量。
- executorNum：本地执行线程的数量。

上述变量可在任意节点通过执行 `rpc(getControllerAlias(), getClusterPerf)` 获得，相关函数介绍请参考 [getClusterPerf](https://docs.dolphindb.cn/zh/funcs/g/getClusterPerf.html)。

若要开启 API 高可用，则需要指定 *highAvailability* 参数为 True，同时通过 *highAvailabilitySites* 指定所有可用节点的地址和端口。

示例脚本如下：

```dolphindb
import dolphindb as ddb
s = ddb.session()
# 创建向量，包含所有可用节点的地址和端口
sites = ["192.168.1.2:24120", "192.168.1.3:24120", "192.168.1.4:24120"]
# 创建连接；开启高可用，并指定sites为所有可用节点的ip:port
s.connect(host="192.168.1.2", port=24120, userid="admin", password="123456", highAvailability=True, highAvailabilitySites=sites)
```

**注意**：

- 若开启高可用后不指定 *highAvailabilitySites*，则默认高可用组为集群全部节点。
- 开启高可用相当于启用自动重连，当连接断开时，如果返回的错误信息为 <NotLeader> 则继续尝试重连连接建立时的节点；如果返回的错误信息为其他，则尝试重连 highAvailabilitySites 列表中上一次成功连接的节点的下一个节点。

## 保活参数 *keepAliveTime*

- **keepAliveTime**：在 TCP 连接状态下两次保活传输之间的持续时间，默认参数为 60，单位秒（s）。

通过配置 *keepAliveTime* 参数可以设置 TCP 的存活检测机制的检测时长，以实现即便在网络不稳定的条件下，仍可及时释放半打开的 TCP 连接。若不指定保活参数 *keepAliveTime*，则默认使用构造 session 时使用的 [*keepAliveTime*（详见 保活参数）](Constructor.html)。指定参数的示例如下：

```dolphindb
import dolphindb as ddb
s = ddb.session()
# 创建连接；设置保活时间为120秒
s.connect(keepAliveTime=120)
```

## 重连参数 *reconnect*, *tryReconnectNums*

- **reconnect**：bool 类型，默认值为 False。在不开启高可用的情况下，是否在 API 检测到连接异常时进行重连。
- **tryReconnectNums**：int 类型，表示重连尝试次数。
  - 若不开启高可用，须与 reconnect 参数搭配使用，对单节点进行有限次重连。若不填写该参数，默认进行无限重连。
  - 当开启 *highAvailability* 高可用参数时，
    - 若指定该参数，将在断开连接后遍历可用节点列表内的每个节点进行有限次重连。一次遍历中，每个节点只会被重连一次，最多进行 *tryReconnectNums* 次遍历尝试。
    - 若不填写该参数，默认是无限重连。

若开启高可用模式，则 API 在检测到连接异常时将自动进行重连，不需要设置参数 *reconnect*。若未开启高可用，通过配置 `reconnect = True`，即可实现 API 在检测到连接异常时进行重连。使用示例如下：

```dolphindb
import dolphindb as ddb
s = ddb.session()
# 创建连接；开启重连
s.connect(host="localhost", port=8848, reconnect=True, tryReconnectNums=5)
```

## 超时参数 *readTimeout*, *writeTimeout*

- **readTimeout**：int 类型，在 TCP 连接状态下的读超时时间，单位为秒（s），默认值为 None，表示无限等待。其对应 TCP 连接的 SO\_RCVTIMEO 选项。
- **writeTimeout**：int 类型，在 TCP 连接状态下的写超时时间，单位为秒（s），默认值为 None，表示无限等待。其对应 TCP 连接的 SO\_SNDTIMEO 选项。

通过配置超时参数，可以设置 TCP 连接的读写超时时间。例如：如果配置读超时时间为 5 秒，而执行一个需要 10 秒才能完成的脚本，则会抛出异常。写超时同理。

## 其他参数

- **startup**：启动脚本。

该参数可以用于执行一些预加载任务。包含加载插件、加载分布式表、定义并加载流数据表等脚本。

```dolphindb
import dolphindb as ddb
s = ddb.session()
# 创建连接；设置启动脚本 "clearAllCache();"
s.connect(host="localhost", port=8848, startup="clearAllCache();")
```
