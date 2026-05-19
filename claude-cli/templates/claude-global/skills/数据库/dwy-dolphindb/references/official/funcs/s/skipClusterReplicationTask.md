---
source_url: https://docs.dolphindb.cn/zh/funcs/s/skipClusterReplicationTask.html
fetched_at: 2026-05-19T09:39:27Z
category: funcs
title: skipClusterReplicationTask
sha1: d672b6473dc627a5be4f56603689437c17b7e27f
---

# skipClusterReplicationTask

## 语法

`skipClusterReplicationTask(taskIds)`

## 详情

用于跳过异步复制任务（通常是由于执行异常导致异步复制停止的任务）。该命令只能由管理员在从集群的控制节点调用。

调用该命令前，需先将集群的异步复制流程暂停（调用 [stopClusterReplication](stopClusterReplication.html) 函数）。执行完该命令后，再重启异步复制（调用 [startClusterReplication](startClusterReplication.html)
命令）。跳过的任务会被标记为完成状态。

## 参数

`taskIds` 标量或向量，表示待跳过的异步复制任务的 id（通过函数 [getMasterReplicationStatus](../g/getMasterReplicationStatus.html) 获取）。

## 例子

```dolphindb
skipClusterReplicationTask(1);
```

相关函数： [startClusterReplication](startClusterReplication.html), [stopClusterReplication](stopClusterReplication.html)
