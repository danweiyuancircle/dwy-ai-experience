---
source_url: https://docs.dolphindb.cn/zh/funcs/s/stopClusterReplication.html
fetched_at: 2026-05-19T09:40:10Z
category: funcs
title: stopClusterReplication
sha1: 3394fac10062c5a5992ba1aaa3c5eaa62e892ac3
---

# stopClusterReplication

## 语法

`stopClusterReplication()`

## 详情

停止集群间的异步复制。该命令只能由管理员在主/从集群的控制节点调用。

- 主集群：调用后，停止将任务放入发送队列。
- 从集群：调用后，停止从主集群读取新任务，但执行中的任务不会停止。

调用该命令前，必须先配置 *replicationMode* 参数。

## 参数

无

## 例子

```dolphindb
stopClusterReplication();
```

相关函数： [startClusterReplication](startClusterReplication.html), [skipClusterReplicationTask](skipClusterReplicationTask.html)
