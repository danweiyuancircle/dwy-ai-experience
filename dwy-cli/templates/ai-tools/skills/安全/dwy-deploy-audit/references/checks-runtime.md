# Deploy Audit — 运行时与韧性检查规则

> **何时读这份：** 当 AI 即将运行 4.6 / 4.8 / 4.9 / 4.10 类检查或解读其输出时读取本文件。

本文件聚焦"运行时与韧性"维度的检查规则、严重度判定与输出格式。涵盖 Docker 安全、自愈与资源耗尽防护、日志大小与防爆、硬件与容器资源。内存和日志的具体数字是冷启动先验，有实测就不用表。

脚本目录简称 `{scripts}` = `../scripts/`。

---

## 4.6 Docker 安全 — `{scripts}/check_docker.sh`

> **跨 skill 联动**:本节发现的镜像版本/镜像源问题,只**报告**不修复。具体修复路径:
> - 镜像 tag 不固定 / `:latest` / 浮动 tag → 引导用户跑 `/dwy-docker`（当次列出 tag 再固定，N-1 只是偏好）
> - daemon 未配 registry-mirrors / 容器用境外 registry → 引导用户跑 `/dwy-mirror-source`（当次探测后取延迟最低的源）

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
| daemon 日志驱动 `log-opts.max-size` | 已配置上限。数字按实测日志增速，不要求 ≤ 100m | high（未配置） |
| **daemon `registry-mirrors`** | 名单里有 daocloud / aliyun / ustc 不算通过。合格看当次对 Registry API 的延迟和内容。未配置时提示去探测，不因为没写某个国内源判失败。私有库或用户指定源不参加公网竞速 | info |
| **运行容器使用境外 registry**(`gcr.io` `ghcr.io` `k8s.gcr.io` `quay.io` `mcr.microsoft.com` `nvcr.io` `docker.elastic.co`)且时区在 PRC | 改用当次探测选出的国内前缀（`registry-mirrors` **不**对它们生效）。DaoCloud 前缀只是当前候选。私有库不改前缀 | high |

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
| Docker daemon `log-opts.max-size` | 已配置上限。数字按本节实测增速，不要求 ≤ 100m | high（未配置） |
| Nginx access.log / error.log 单文件 | < 500 MB | high |
| `/etc/logrotate.d/nginx` | 存在 | high |
| `journalctl --disk-usage` | < 2 GB | medium / high(≥ 2 GB 且 SystemMaxUse 未配) |
| `/etc/systemd/journald.conf` `SystemMaxUse` | 已显式配置 | low |
| 应用日志目录（`/var/log/<svc>` / `/opt/*/logs` / `/home/*/logs` / `/srv/*/logs`） | 列出 Top 10 供人工核对 | info |
| 日志按当前 docker 容器存活时长粗估的撑天数 | 按实测增速，写满根盘前有人处理。30 / 90 天是告警线，不是要配成的保留天数 | high(<90) / critical(<30) |

**输出规约：** 脚本会汇总 `Docker json-log + Nginx + journal + 应用日志` 总占用，对照根盘可用空间，给出"按 docker 当前增速预计可撑 N 天"的粗估。粗估只算 docker json-log 增量，不含数据库/应用日志业务增量，因此**结论偏乐观**，作为下限警示使用。

---

## 4.10 硬件识别与资源 — `{scripts}/check_capacity.sh`

脚本输出宿主规格、容器硬限、`docker stats` 单帧占用、Postgres/Redis 参数、compose 声明、日志日增量能对上的根盘剩余。报告写「本次实测 vs 当前硬限」。**禁止**把下面的数字写成应改成的配额。

必须成立的只有这些：

- 每个容器有内存硬限。关键服务（redis / postgres / mysql / mongo / clickhouse / elasticsearch）没有就是 high
- Redis 设了 `maxmemory`，且容器 `mem_limit` 大于它。未设或为 0 是 **critical**
- Postgres `shared_buffers` 不超过宿主总内存的 50%。这是 OOM 天花板，不是目标比例
- 容器硬限合计不超过宿主总内存的 75%。超过则 OS 没有余量，是 high。不要求贴近 65%
- 日志有 `max-size` 和 `max-file`。两边都没有是 **critical**
- 按 `check_logs.sh` 的实测日增量，根盘会在短时间内写满，才收紧轮转。30 天 critical，90 天 high。这是告警线

有 `docker stats` 或日志日增量时，用实测：

- 内存硬限低于这一帧占用（或已有的监控峰值）才要加。单帧不是峰值，报告里写明
- 硬限远高于占用，不是问题，不要为了贴近下表去改小
- 日志配额按日增量和根盘剩余算。`max-size × max-file × 容器数` 本身就能占掉根盘约 5% 以上，说明天花板太高，是 high。5% 是安全天花板，不是目标占用

没有占用、也没有日志增量（服务刚起）时，才用下面的冷启动先验。服务跑起来之后以实测替换，不把先验写回本文件。

**冷启动先验：内存（没有实测时才用）**

| 宿主总内存 | Backend mem_limit | Postgres mem_limit / shm_size / shared_buffers / effective_cache_size | Redis mem_limit / maxmemory |
|-----------|-------------------|--------------------------------------------------------------------|----------------------------|
| 2 GB | 384m | 512m / 128m / 128MB / 384MB | 256m / 180mb |
| 4 GB | 1g | 1g / 256m / 256MB / 768MB | 384m / 256mb |
| 8 GB | 2g | 2g / 512m / 512MB / 1536MB | 768m / 512mb |
| 16 GB | 4g | 4g / 1g / 1GB / 3GB | 1g / 700mb |

比例只解释这张先验怎么来的：硬限合计大约留出 OS 余量；Postgres `shared_buffers` 约容器硬限的 25%，`effective_cache_size` 约 75%；Redis `maxmemory` 约容器硬限的 70%，其余给 fork 时的写时复制。实测对不上就丢掉整行。

**对比报告格式**

```
| 服务 | 配置项 | 本次实测 | 当前硬限 | 状态 |
|------|--------|----------|----------|------|
| backend | mem | stats 420MiB（单帧） | 无 | 缺上限 |
| db | mem | stats 300MiB（单帧） | 1g | 硬限高于实测 |
| db | shared_buffers | — | 超过宿主 50% | 撞上天花板 |
| redis | maxmemory | 当前占用 | 0 | 未设 |
```

没有实测的新机器，在「本次实测」列写「无，用冷启动先验 &lt;数字&gt;」，并注明服务跑起来后要重测。

**严重等级**

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 关键服务容器无 `mem_limit` | 已设置 | high |
| 硬限低于本次 `docker stats` 占用 | 硬限高于实测 | high |
| Redis `--maxmemory` 未设置或 `0` | 已设置，且小于容器 `mem_limit` | **critical** |
| Postgres `shared_buffers` > 宿主总内存 50% | 不超过 | high |
| Redis 未启用 AOF（`--appendonly yes`） | 按持久化需求，不是配额 | medium |
| 容器 `mem_limit` 合计 > 宿主总内存 75% | 不超过。低于 75% 不要求再贴近某个比例 | high |

偏离冷启动先验表 **不是** 违规。

---

### 日志轮转

有日增量时用增速和根盘剩余决定 `max-size` / `max-file`。没有增量时才看冷启动先验。

**冷启动先验：daemon `log-opts`（没有日志增量时才用）**

| 宿主规格 | 根盘 | 容器数(估) | `max-size` | `max-file` | 单容器 quota | 备注 |
|---------|------|-----------|------------|-----------|-------------|------|
| 入门 | < 50 GB | 任意 | `10m` | `3` | ~30 MB | 盘小，先验从紧 |
| 标准 | 50-150 GB | ≤ 5 | `50m` | `5` | ~250 MB | 无增速时的起点 |
| 标准 | 50-150 GB | > 5 | `20m` | `5` | ~100 MB | 容器多，先验收紧 |
| 大型 | > 150 GB | 任意 | `100m` | `5` | ~500 MB | 无增速时的起点 |

容器级 `logging.options` 盖过 daemon。库、反代、应用的保留条数不一样，同样只在没有该容器增速时参考，不作为合格线。

字段写法示例（数字不是目标配额）：

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "<当次算出的大小>",
    "max-file": "<当次算出的个数>",
    "compress": "true"
  }
}
```

**严重等级**

| 判定 | 严重级 |
|------|--------|
| daemon 无 `log-opts.max-size` 且容器也无 `LogConfig.Config` | **critical** |
| 容器无单独 `LogConfig.Config`，daemon 已有上限 | 通过（走 daemon） |
| `max-size × max-file × 容器数` > 根盘约 5% | high（配额天花板太高） |
| 按实测日增量，不足 90 天写满根盘 | high；不足 30 天为 **critical** |
| 当前 `max-size` 与冷启动先验不同 | 不是问题 |
