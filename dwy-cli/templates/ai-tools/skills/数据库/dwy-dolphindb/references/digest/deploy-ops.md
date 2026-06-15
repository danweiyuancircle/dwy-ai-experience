---
title: 部署与运维
category: digest
covers: [deploy, sys_man, funcs/b/backup, funcs/r/restore, cluster_async_replc]
---

# 部署与运维

## 何时用

- 选型阶段：决定单节点 / 单机集群 / 多机集群 / 多机 HA 集群
- 上线前：规划节点角色与端口、配置 HA、制定备份策略
- 日常运维：扩容、升级、备份恢复、监控、异地容灾（异步复制）
- 故障处置前：先看本文「错误操作禁忌表」，避免破坏元数据导致数据不可恢复

## 部署形态对比

| 形态 | 控制节点 | 数据节点 | 计算节点 | HA | 适用场景 |
| --- | --- | --- | --- | --- | --- |
| 单节点（standalone） | 不分离，全在一进程 | 同左 | — | 无 | 开发、研究、小规模生产 |
| 单机集群（single-machine cluster） | 1 | N（同机） | 0~N | 数据多副本可有 | 单机但需扩展节点、本地多副本 |
| 多机集群（multi-machine cluster） | 1 | N（跨机） | 0~N | 数据多副本可有 | 一般生产 |
| 多机 HA 集群 | 3+（Raft 仲裁） | N（跨机） | 0~N | 元数据 + 数据 + API 三层 HA | 企业级关键业务 |

> 单节点不支持扩展和高可用，集群模式可扩展并支持 HA。

## 节点角色

| 角色 | 数量约束 | 职责 |
| --- | --- | --- |
| controller（控制节点） | 单集群 1 个；HA 集群 3+ | 收集 agent/data node 心跳；管理 DFS 元数据、事务日志；调度任务 |
| agent（代理节点） | 每台物理机有且仅有 1 个 | 执行 controller 下发的 start/stop 命令，拉起/关停本机的 data node 和 compute node |
| data node（数据节点） | 每机可多个 | 存储数据；同时承担查询、计算 |
| compute node（计算节点） | 每机 0 ~ 多个 | 仅响应客户端查询/计算请求，不存储；实现存算分离 |

> 计算节点用于把计算压力从 data node 上剥离。需要跨节点并行时，compute node 通过 controller 协调多 data node 拉数据。

## 关键端口（默认）

| 端口 | 用途 | 说明 |
| --- | --- | --- |
| 8848 | 单节点 / controller 监听端口（默认） | Web 管理工具、客户端连接同一端口 |
| 8900+ | data node / agent / compute node 端口 | 由 `cluster.nodes` 配置文件分配 |

> 多机部署时，所有节点之间需双向开通 TCP；防火墙限制是新人最常踩的坑（节点显示 isAlive=false）。

## HA 配置要点（多机 HA 集群）

- **控制节点**：至少 3 个（推荐 3 或 5），通过 Raft 协议选主，半数以上存活才可写元数据
- **数据副本**：`dfsReplicationFactor=2` 起步（推荐 3），副本分布在不同物理机（`dfsReplicaReliabilityLevel=1` 强制跨节点）
- **API HA**：客户端 / API SDK 配置多个控制节点地址列表，控制节点切主后客户端自动重连
- **事务日志（redo log）**：所有 data node 必须开启 redo log，崩溃恢复依赖它

## 备份恢复

**严禁 cp 文件备份数据库**：DolphinDB 的 chunk 元数据由 controller 维护，直接拷贝数据目录会让元数据和数据不一致，集群级损坏不可逆。

使用官方函数：

| 函数 | 用途 | 关键参数 |
| --- | --- | --- |
| `backup(backupDir, dbPath\|sqlObj, force=false, parallel=false, snapshot=true)` | 按分区备份分布式表 | `force=true` 全量；`snapshot=true` 同步删除主库已删的分区 |
| `backupDB(backupDir, dbPath)` | 按库备份 | 整库 |
| `backupTable(backupDir, tableObj)` | 按表备份 | 单表 |
| `restore(backupDir, dbPath, tableName, partition, force)` | 按分区恢复 | 支持指定分区子集恢复 |
| `restoreDB / restoreTable` | 按库 / 按表恢复 | — |

支持本地路径、AWS S3（路径以 `s3://` 开头，需 `preloadModules=plugins::awss3` + S3 凭证配置）。Linux 下可通过 `keyPath` 参数指定加密密钥。

## 错误操作禁忌表

| 禁忌操作 | 后果 | 正确做法 |
| --- | --- | --- |
| `cp -r /storage/CHUNKS/...` 备份数据目录 | 元数据与数据不一致，恢复时分区丢失 | `backup()` / `backupDB()` |
| 手工删 redo log（`/log/*.redo`） | 崩溃恢复失败，节点起不来 | 等节点正常关闭后日志自动回收 |
| `kill -9` 强杀 data node | 进行中事务可能丢失或元数据不一致 | Web 管理工具 stopDataNode；脚本 `stopDataNode` 函数 |
| 不停服改 hostname / ip | controller 心跳认不出节点，集群分裂 | 停集群 → 改 host → 改 `cluster.nodes` → 启 |
| 直接删 DFS 表对应的目录 | 元数据残留，无法 drop 也无法重建同名表 | `dropTable / dropDatabase / dropPartition` 函数 |
| 控制节点只部署 2 个 | Raft 无法选主，故障即失去元数据写能力 | HA 控制节点 3 / 5 个奇数 |
| 单副本 + 单机宕机 | 数据永久丢失 | `dfsReplicationFactor>=2`，副本跨机 |
| 异步复制中跳过任务但不查原因 | 主从永久不一致 | 先 `getSlaveReplicationStatus` 看失败原因，处理后 `startClusterReplication` 重启；最后才用 `skipClusterReplicationTask` |

## 升级流程（标准滚动）

1. 备份：`backup()` 全量备份关键库 + 导出配置文件（`cluster.cfg / cluster.nodes / agent.cfg`）
2. 停服：Web 管理工具或脚本 `stopDataNode` 优雅停 data node，再停 controller，最后停 agent
3. 替换：解压新版 `server/` 目录，**保留**旧的 `dolphindb.lic`、`config/`、`data/`、`log/`
4. 配置：对比新版 `cluster.cfg.example` 是否有新增项，按需合入
5. 启动：先 agent → controller → 集群管理页面启动 data node / compute node
6. 校验：
   - Web 集群管理页面所有节点 `isAlive=true`
   - 跑一遍 smoke test：`select count(*) from loadTable("dfs://...","...")`、写入测试、备份还原测试
   - 检查 `log/*.log` 无 ERROR

> HA 集群滚动升级：3 个 controller 逐一升级，每次升级前确认其余 2 个健康。

## 监控告警信号清单

| 信号源 | 关注指标 | 告警阈值（建议） |
| --- | --- | --- |
| `getClusterPerf()` | 各节点 CPU / 内存 / 磁盘 / 网络 | CPU > 80% 持续 5min；内存 > 90% |
| `getClusterChunksStatus()` | chunk 副本数、状态 | 副本数 < 配置值；存在 `RECOVERING` 持续 > 30min |
| `getRecoveryTaskStatus()` | 恢复任务队列长度 | 持续增长不下降 |
| `getJobStat()` / `getConsoleJobs()` | 长跑作业 | 单作业 > 业务 SLA |
| log 文件 | ERROR / FATAL 关键字 | 任意 ERROR 立即告警 |
| `getSlaveReplicationStatus()` | 异步复制 lag | lag > 业务容忍上限（如 5 分钟）|
| Raft leader 切换日志 | 频繁切主 | 1 小时内 ≥ 2 次 |

## 异步复制（异地容灾）

- 用途：主集群 → 从集群单向异步同步，主集群挂了从集群可继续提供读
- 启用：主集群数据节点调 `setDatabaseForClusterReplication("dfs://xxx", true)`，每次一个库
- 工作流：主集群提交事务后，把已完成事务的元数据放入发送队列；从集群按 taskID 偏移量拉取并执行
- 仅支持分布式表（不支持内存表、本地磁盘表）
- 不支持权限管理、分级存储、存储引擎修改等非 DDL/DML
- 故障处理：从集群多次失败导致中断 → `getSlaveReplicationStatus` 查原因 → 处理后 `startClusterReplication` 重启 → 实在过不去再 `skipClusterReplicationTask` 跳过
- 停止：主从都调 `stopClusterReplication()`；停单库用 `setDatabaseForClusterReplication("dfs://xxx", false)`
- 注意：从集群新增节点后，哈希算法仍基于原节点数映射，新节点不会分到任务

## 下钻原文路径

- 部署总览：`official/deploy/deploy_intro.md`
- 单节点部署：`official/tutorials/standalone_server.md`
- 单机集群部署：`official/tutorials/single_machine_cluster_deploy.md`
- 多机集群部署：`official/tutorials/multi_machine_cluster_deployment.md`
- 高可用集群部署：`official/tutorials/ha_cluster_deployment.md`
- 集群管理（扩容 / 升级）：`official/sys_man/cluster_manage.md`
- 多集群管理：`official/sys_man/multi_cluster_management.md`
- 异步复制：`official/sys_man/cluster_async_replc.md`
- 备份恢复函数：`official/funcs/b/backup.md`、`backupDB.md`、`backupTable.md`、`backupsettings.md`
- 恢复函数：`official/funcs/r/restore.md`、`restoreDB.md`、`restoreTable.md`、`restoresettings.md`
- License 指纹：`official/deploy/license_fingerprint_collection.md`
- 错误码：`official/error_codes/`
