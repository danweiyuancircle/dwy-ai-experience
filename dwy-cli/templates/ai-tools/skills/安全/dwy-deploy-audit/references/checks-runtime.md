# Deploy Audit — 运行时与韧性检查规则

> **何时读这份：** 当 AI 即将运行 4.6 / 4.8 / 4.9 / 4.10 类检查或解读其输出时读取本文件。

本文件聚焦"运行时与韧性"维度的检查规则、严重度判定与输出格式。涵盖 Docker 安全、自愈与资源耗尽防护、日志大小与防爆、硬件识别与资源推荐。

脚本目录简称 `{scripts}` = `../scripts/`。

---

## 4.6 Docker 安全 — `{scripts}/check_docker.sh`

> **跨 skill 联动**:本节发现的镜像版本/镜像源问题,只**报告**不修复。具体修复路径:
> - 镜像 tag 不固定 / `:latest` / 浮动 tag → 引导用户跑 `/dwy-docker`(走 query_dockerhub.py 选 N-1 minor)
> - daemon 未配 registry-mirrors / 容器用境外 registry → 引导用户跑 `/dwy-mirror-source`(写阿里云/中科大/daocloud)

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `/var/run/docker.sock` 挂载到容器 | 仅可信容器 | **critical** |
| 容器以 root 运行 | 应使用非 root user | high |
| 端口绑定 | DB/Redis 等内部服务**不应** `0.0.0.0:5432` 暴露 | **critical** |
| 镜像 tag = `:latest` 或省略 tag | 固定到具体 patch | **critical** |
| 镜像 tag = 浮动 tag(`:stable` `:mainline` `:alpine` `:bookworm` `:slim` `:edge` `:nightly` 等) | 固定到具体 patch | high |
| 镜像 tag = 仅 major(`:7` `:16`) | 至少到 minor,推荐到 patch | high |
| 镜像 tag = `major.minor`(`:7.4`)| 固定到 patch(`:7.4.9`) | medium |
| 镜像 tag = `@sha256:...` digest | — | OK 加分 |
| `--privileged` 容器 | 无 | **critical** |
| Docker 版本 | 非已知 CVE 版本 | medium |
| Docker daemon 远程 API | 未暴露 2375/2376 公网 | **critical** |
| 容器 `RestartPolicy` | `always` 或 `unless-stopped`（**服务器重启后自动起来**） | **critical** |
| 容器 `RestartPolicy=no` 但正在 running | 不允许（重启会丢） | **critical** |
| 容器 `RestartPolicy=on-failure` | 不推荐（手动 stop / OOM 后不会重启） | high |
| daemon 日志驱动 `log-opts.max-size` | 已配置（≤ 100m，防容器日志写满磁盘） | high |
| **daemon `registry-mirrors`**(时区在 PRC 时) | 至少 1 个国内源(daocloud / aliyun / ustc / tsinghua) | high(PRC 无配置)/ info(境外) |
| **运行容器使用境外 registry**(`gcr.io` `ghcr.io` `k8s.gcr.io` `quay.io` `mcr.microsoft.com` `nvcr.io` `docker.elastic.co`)且时区在 PRC | 改用 `<registry>.m.daocloud.io` 前缀(`registry-mirrors` **不**对它们生效) | high |

**Docker 版本与暴露面判定补充：**

- 官方基础文档：
  - Engine security：`https://docs.docker.com/engine/security/`
  - daemon remote access：`https://docs.docker.com/engine/daemon/remote-access/`
  - logging driver：`https://docs.docker.com/engine/logging/configure/`
  - OWASP Docker Security Cheat Sheet：`https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html`
- 版本安全搜索词：
  - `docker engine <version> CVE`
  - `docker <version> security advisory`
- 分级规则：
  - 命中 **CISA KEV**，或 Docker daemon TCP 端口公网暴露且无充分保护 → **critical**
  - 命中高危 CVE（建议按 CVSS ≥ 7.0 参考），但当前未见在野利用 → high
  - 未命中高危 CVE，但版本过旧且缺少持续维护依据 → medium
- `docker.sock` 挂载、`--privileged`、2375/2376 暴露属于**配置暴露面**，优先按当前表里的配置项分级，不要被“版本没问题”掩盖。

---

## 4.8 自愈与资源耗尽防护 — `{scripts}/check_resilience.sh`

服务器意外重启后能否自动恢复，以及在异常负载下能否守住底线。

**B. 系统服务开机自启**（默认清单 + 自动探测）

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `sshd` is-enabled | enabled（不起就再也连不上） | **critical** |
| `nginx` is-enabled | enabled | **critical** |
| `docker` is-enabled | enabled（影响所有容器） | **critical** |
| `postgresql` is-enabled | enabled | **critical** |
| `redis` / `redis-server` is-enabled | enabled | high |
| `frps` / `frpc` is-enabled（如部署） | enabled | high |
| `fail2ban` is-enabled（如安装） | enabled | medium |
| 应用主进程 systemd unit | enabled | **critical** |
| running 但 disabled 的服务 | 不应存在（重启即丢失） | high |
| 自动探测：`systemctl list-unit-files --state=enabled` | 输出供人工核对应用进程是否在内 | info |

**D. 资源耗尽防护**

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `swap` 已配置 | ≥ 1GB（OOM 缓冲） | medium |
| 根分区使用率 | < 80% | medium（≥ 90% critical） |
| `/etc/logrotate.conf` 存在 | 是 | high |
| 关键服务有 `/etc/logrotate.d/<name>` | nginx / postgresql / redis 等都应有 | high |
| nginx / postgres / redis 进程 `ulimit -n` | ≥ 4096，建议 65535 | medium |
| `/proc/pressure/memory`（PSI） | 输出供观察当前内存压力 | info |
| 容器 `HostConfig.Memory` | 关键容器应有内存上限 | medium |

---

## 4.9 日志大小与防爆检查 — `{scripts}/check_logs.sh`

防止日志写满磁盘把整机拖垮。check_resilience.sh 的 D 节给的是宏观信号（`/var/log` 总大小、logrotate 是否存在），本节按"日志源"细化到单文件粒度，并基于容器存活时长粗估"撑天数"。

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| Docker 单容器 `*-json.log` 大小 | < 500 MB（daemon 配 log-opts max-size 时自动控） | high(>500 MB) / critical(>1 GB 且 daemon 无 log-opts) |
| 容器自身 `LogConfig.Config` 覆盖 | 至少有 `max-size`，否则继承 daemon | high（容器 + daemon 都没配） |
| Docker daemon `log-opts.max-size` | 已配置 ≤ 100m | high（同 check_docker.sh，本节关联展开） |
| Nginx access.log / error.log 单文件 | < 500 MB | high |
| `/etc/logrotate.d/nginx` | 存在 | high |
| `journalctl --disk-usage` | < 2 GB | medium / high(≥ 2 GB 且 SystemMaxUse 未配) |
| `/etc/systemd/journald.conf` `SystemMaxUse` | 已显式配置 | low |
| 应用日志目录（`/var/log/<svc>` / `/opt/*/logs` / `/home/*/logs` / `/srv/*/logs`） | 列出 Top 10 供人工核对 | info |
| 日志按当前 docker 容器存活时长粗估的撑天数 | > 90 天 | high(<90) / critical(<30) |

**输出规约：** 脚本会汇总 `Docker json-log + Nginx + journal + 应用日志` 总占用，对照根盘可用空间，给出"按 docker 当前增速预计可撑 N 天"的粗估。粗估只算 docker json-log 增量，不含数据库/应用日志业务增量，因此**结论偏乐观**，作为下限警示使用。

---

## 4.10 硬件识别与资源推荐 — `{scripts}/check_capacity.sh`

> 脚本只输出 raw（硬件规格 + 当前容器 mem_limit + Postgres/Redis 启动参数 + compose 资源声明）；主 Claude 用下表生成 "推荐 vs 当前" 对比报告。详细推荐规则与配比公式参考 `dwy-docker` skill 第二部分。

**容器资源推荐分级表（按宿主总内存）**

| 宿主总内存 | Backend mem_limit | Postgres mem_limit / shm_size / shared_buffers / effective_cache_size | Redis mem_limit / maxmemory |
|-----------|-------------------|--------------------------------------------------------------------|----------------------------|
| 2 GB | 384m | 512m / 128m / 128MB / 384MB | 256m / 180mb |
| 4 GB | 1g | 1g / 256m / 256MB / 768MB | 384m / 256mb |
| 8 GB | 2g | 2g / 512m / 512MB / 1536MB | 768m / 512mb |
| 16 GB | 4g | 4g / 1g / 1GB / 3GB | 1g / 700mb |

**配比原则**

- 容器 `mem_limit` 合计 ≤ 宿主总内存的 **65%**（预留 OS / 全局 nginx / 监控 agent / frpc 等）
- Postgres `shared_buffers` = 容器 `mem_limit` 的 **25%**
- Postgres `effective_cache_size` = 容器 `mem_limit` 的 **75%**
- Redis `maxmemory` = 容器 `mem_limit` 的 **70%**（剩 30% 给 RDB/AOF fork 时 COW 留 buffer）
- Redis `mem_limit` = `maxmemory ÷ 0.7` 向上取整

**对比报告格式（主 Claude 在报告里生成）**

```
| 服务 | 配置项 | 推荐(基于 X GB 宿主) | 当前 | 状态 |
|------|--------|--------------------|------|------|
| backend | mem_limit | 1g | 无 | ❌ 缺失 |
| db | mem_limit | 1g | 1g | ✅ |
| db | shared_buffers | 256MB | 128MB(默认) | ⚠️ 偏低 |
| db | shm_size | 256m | 64m(默认) | ⚠️ 偏低 |
| redis | maxmemory | 256mb | 256mb | ✅ |
| redis | mem_limit | 384m | 384m | ✅ |
| redis | appendonly | yes | no | ⚠️ 重启丢数据 |
```

**严重等级标记规则**

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 关键服务（redis / postgres / mysql / mongo / clickhouse / elasticsearch）容器无 `mem_limit` | 已设置 | high |
| Redis `--maxmemory` 未设置或 `0` | 已设置 | **critical** |
| Postgres `shared_buffers` > 宿主总内存 50% | ≤ 宿主总内存 50% | high |
| Postgres `shm_size` < 128m | ≥ 256m | medium |
| Redis 未启用 AOF（`--appendonly yes`） | yes | medium |
| 容器 `mem_limit` 合计 > 宿主总内存 75% | ≤ 65% | high |
| `mem_limit` 偏离推荐表 ±50% 以上（主 Claude 判定） | 在分级表区间内 | medium |

---

### 日志大小推荐分级表（防容器日志无限增长撑爆磁盘）

依据是 `<根盘容量>` × `<容器规模>`,**单容器最大日志占用 = `max-size` × `max-file`**;所有容器日志合计应 ≤ 根盘可用空间的 **5%**(留磁盘给数据/swap/OS)。

**daemon 兜底配置(`/etc/docker/daemon.json` `log-opts`)**

| 宿主规格 | 根盘 | 容器数(估) | `max-size` | `max-file` | 单容器 quota | 备注 |
|---------|------|-----------|------------|-----------|-------------|------|
| 入门 | < 50 GB | 任意 | `10m` | `3` | ~30 MB | 2-4 GB VM 入门款,日志少留磁盘 |
| 标准 | 50-150 GB | ≤ 5 | `50m` | `5` | ~250 MB | 4-8 GB VM 通用 |
| 标准 | 50-150 GB | > 5 | `20m` | `5` | ~100 MB | 容器多则降单容器 quota |
| 大型 | > 150 GB | 任意 | `100m` | `5` | ~500 MB | 16+ GB 服务器,空间充裕 |

**容器级覆盖(compose `logging.options`,优先于 daemon)**

| 容器类型 | `max-size` | `max-file` | 理由 |
|---------|-----------|-----------|------|
| 数据库 (postgres / mysql / mongo) | `20m` | `10` | 慢查询日志价值高,保留更多滚动 |
| Web 反代 (nginx access log 走 stdout) | `50m` | `5` | 写入量大,单文件可放宽 |
| 应用后端 (FastAPI / Node 等) | `10m` | `5` | 通用 |
| Redis / 缓存类 | `10m` | `3` | 写入少,保留少 |

**daemon.json 模板**

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5",
    "compress": "true"
  }
}
```

**严重等级标记(脚本侧 + 主 Claude 对照表)**

| 判定 | 严重级 |
|------|--------|
| daemon 无 `log-opts.max-size` 且容器也无 `LogConfig.Config` | **critical** |
| daemon `max-size` > 推荐档 50% 以上(如根盘 < 50 GB 用 100m) | high |
| 容器无 `LogConfig.Config` 但 daemon 有兜底 | OK(走 daemon) |
| 容器 `LogConfig.Config` 设了但 max-size 偏离推荐档 ±50% | medium |
| 估算所有容器日志合计 > 根盘可用 5% | high |
