---
source_url: https://docs.dolphindb.cn/zh/funcs/c/copyReplicas.html
fetched_at: 2026-05-19T09:15:54Z
category: funcs
title: copyReplicas
sha1: 6722b344914316b71682513e974859a3021e031d
---

# copyReplicas

## 语法

`copyReplicas(srcNode, destNode, chunkId)`

## 详情

把源节点上的一个或多个 chunk 的副本复制到目标节点。如果目标节点上已经存在该 chunk，那么系统将忽略本次操作。该命令只能由管理员在控制节点上执行。

通过 [getRecoveryTaskStatus](../g/getRecoveryTaskStatus.html)
函数可以查看任务状态。

## 参数

**srcNode** 是一个字符串，表示源节点的别名。

**destNode** 是一个字符串，表示目标节点的别名。

**chunkId** 是字符串标量或向量，表示 chunk 的 ID。

## 返回值

无。

## 例子

把 "node1" 上所有 chunk 的副本复制到 "node2"。

```dolphindb
chunkIds=exec chunkId from pnodeRun(getChunksMeta) where node="node1"
copyReplicas("node1", "node2", string(chunkIds));
```
