# Docker 部署（v3 Alpine 镜像）

## 已知坑（按踩坑频次）

| 问题 | 表现 | 解决 |
|---|---|---|
| 镜像里没有 `curl` | healthcheck `curl: not found` | 用 `wget` 替代 |
| `localhost` 解析到 IPv6 ::1，DDB 只监听 v4 | healthcheck 连不上 | 改 `127.0.0.1` |
| macOS 宿主无 `/etc/hostname` `/etc/machine-id` | 启动报 mount 失败 | 不要 mount 这两个文件 |
| 自定义 `dolphindb.cfg` 写了 `logFile`/`volumes` 路径 | 与 Docker volume 冲突 → 数据写错位置 | 只覆盖必要参数（如 `maxMemSize`），其余用默认 |
| `dataSync` 和 `CacheEngine` 只开一个 | 启动失败或数据异常 | 要开都开，要关都关。开发环境**都不配**用默认值 |
| 服务名 vs localhost | 后端 `localhost:8848` 连不到容器内的 DDB | 用 Docker 服务名 `dolphindb:8848` |

## 标准 healthcheck

```yaml
services:
  dolphindb:
    image: dolphindb/dolphindb:v3.00.x-alpine
    ports:
      - "8848:8848"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- --timeout=3 http://127.0.0.1:8848/ || exit 1"]
      start_period: 30s    # DDB 初始化慢，给足时间
      interval: 5s
      timeout: 5s
      retries: 10
    deploy:
      resources:
        limits:
          memory: 8G       # 社区版硬上限
          cpus: '2'        # 社区版硬上限
```

## 后端连接 env 模板

```bash
# 容器间用服务名，不要 localhost
DOLPHINDB_HOST=dolphindb
DOLPHINDB_PORT=8848
DOLPHINDB_USER=admin
DOLPHINDB_PASSWORD=改成你的强密码
DOLPHINDB_POOL_SIZE=2           # 2 核机器经验值，不是协议层 512 的上限
DOLPHINDB_KEEPALIVE=120         # 长查询调高，默认 30s 容易断
```

`DOLPHINDB_POOL_SIZE` 取值：4 worker → pool size 3。设大没收益（worker 是 4），还可能挤占 web/管理。

## 配置最小化

只覆盖**必须**的几个参数，其余用镜像默认：

```ini
# dolphindb.cfg（minimal）
maxMemSize=6                    # 留 2GB 给 OS
workerNum=4                     # CPU 核数 × 2
chunkCacheEngineMemSize=1       # 列缓存上限
TSDBCacheEngineSize=0.5         // TSDB 写缓存
```

**别动**：`logFile`、`volumes`、`dfsMetaDir`、`chunkMetaDir`、`persistenceDir`、`TSDBRedoLogDir` —— 这些和 Docker volume 挂载位置耦合，改了启动失败或数据丢失。

跨引用：连接配置 → [[setup-and-connection]]，性能调优 → [[performance-tuning]]。
