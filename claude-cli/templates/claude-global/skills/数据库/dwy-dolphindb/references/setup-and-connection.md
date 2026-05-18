# 连接与基础设置

## 集群拓扑

```
controller (8848)  ←─ Web UI / DolphinDB GUI / Python SDK 入口
    │
    ├── datanode-1 (8849?)   ← 实际存储 + 计算
    └── datanode-2 (8850?)   ← 实际存储 + 计算
```

社区版默认 1 控 2 节点。`localhost:8848` 是控制节点的 Web 端，**Python SDK 连这里**，由控制节点路由到数据节点。

查实际端口和节点：

```dolphindb
getClusterPerf()                 // 列出所有节点 name/host/port/mode
getControllerAlias()             // 控制节点别名
getDataNodes()                   // 数据节点列表
```

## Python SDK 安装

```bash
pip install dolphindb==3.0.4
# 验证
python -c "import dolphindb as ddb; print(ddb.__version__)"
```

## 标准连接

```python
import dolphindb as ddb

s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")

# 验证
print(s.run("getNodeAlias()"))
```

### 完整 connect 签名

```python
connect(host, port,
        userid=None, password=None, startup=None,
        highAvailability=False, highAvailabilitySites=None,
        keepAliveTime=None, reconnect=False,
        *,
        tryReconnectNums=None, readTimeout=None, writeTimeout=None)
```

### 大查询场景（必须调）

```python
s.connect(
    "localhost", 8848, "admin", "123456",
    keepAliveTime=120,        # 默认 30s，大查询要拉到 ≥120s 否则断连
    reconnect=True,
    tryReconnectNums=5,
    readTimeout=600,          # 单位秒，大结果集别用默认
    writeTimeout=600,
)
```

### 高可用（连节点池，自动选最低负载）

```python
s = ddb.session()
sites = ["localhost:8848", "192.168.0.107:8848"]   # 控制节点列表
s.connect(
    host="localhost", port=8848,
    userid="admin", password="123456",
    highAvailability=True,
    highAvailabilitySites=sites,
)
```

### 启动脚本（每次连接自动跑）

```python
s.connect(host="localhost", port=8848,
          startup="clearAllCache(); login('admin','123456')")
```

## 关闭连接

```python
s.close()
```

**重要**：连接不显式关，连接数会被快速吃满（社区版上限 512，当前已用 15）。脚本结束务必 `s.close()`，长服务用 `try/finally`。

## DBConnectionPool（并发场景必备）

```python
pool = ddb.DBConnectionPool(
    "localhost", 8848, threadNum=3,    # 4 worker → pool size 3
    userId="admin", password="123456",
)

# 并发跑多个 SQL
import asyncio
loop = asyncio.get_event_loop()
tasks = [pool.run(f"select * from loadTable('dfs://k','k_minute') where SecurityID=`{sid}`")
         for sid in ['600000', '600036']]
results = loop.run_until_complete(asyncio.gather(*tasks))

pool.shutDown()
```

**社区版 worker = 4**：pool size 取 3（留 1 worker 给 Web/管理）。设到 4+ 会和 web/ops 抢线程。

## 登录与权限

```python
# 方式 1：connect 时带凭证（推荐）
s.connect("localhost", 8848, "admin", "123456")

# 方式 2：先连后登录
s.connect("localhost", 8848)
s.login("admin", "123456")

# 改密码
s.run("changePwd('admin', '新密码')")
```

## 常见报错

| 报错 | 原因 | 处理 |
|---|---|---|
| `Connection refused` | 节点没起 / 端口不对 | `lsof -i:8848` 看端口；查 `getClusterPerf()` 用控制节点端口 |
| `Couldn't send script/function...` | `keepAliveTime` 太短，长查询被踢 | 提到 120+ |
| `The user is not authorized to perform this operation` | 权限不够 | 用 admin 登录或 `grant(...)` |
| `Out of memory` | 单查询超 2GB | 看 [[performance-tuning]] |
| `Couldn't connect to the gateway` | 高可用模式所有 site 都挂 | 退回单节点模式排查 |
| Python 端 hang 住 | 服务端作业卡了 | 另起 session 跑 `getConsoleJobs()` 找 → `cancelConsoleJob()` |

## Web UI 入口

- 控制台：http://localhost:8848
- 看作业 / 节点状态 / 配置参数 / 用 Web 编辑器跑脚本
- 局域网访问用机器 IP：`http://192.168.0.107:8848`
