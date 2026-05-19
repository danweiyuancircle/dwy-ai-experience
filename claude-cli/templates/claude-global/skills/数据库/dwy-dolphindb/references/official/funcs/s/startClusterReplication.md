---
source_url: https://docs.dolphindb.cn/zh/funcs/s/startClusterReplication.html
fetched_at: 2026-05-19T09:39:57Z
category: funcs
title: startClusterReplication
sha1: 02c3ddbb6b19a90126d3a7d6566bf841c0dff0fa
---

# startClusterReplication

## 语法

`startClusterReplication()`

## 详情

重启由多次任务失败而停止或调用 [stopClusterReplication](stopClusterReplication.html) 主动停止的异步复制。该命令只能由管理员在主/从集群的控制节点调用。调用该命令前，必须先配置
*replicationMode* 参数。

## 参数

无

## 例子

```dolphindb
startClusterReplication();
```

相关函数： [stopClusterReplication](stopClusterReplication.html), [skipClusterReplicationTask](skipClusterReplicationTask.html)
