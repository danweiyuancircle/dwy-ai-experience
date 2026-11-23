---
source_url: https://docs.dolphindb.cn/zh/funcs/d/deleteReplicas.html
fetched_at: 2026-05-19T09:18:38Z
category: funcs
title: deleteReplicas
sha1: b37e96680e5de649da66fd41f4e3997ada94f426
---

# deleteReplicas

## 语法

`deleteReplicas(chunkId, nodeAlias)`

## 详情

把节点上的一个或多个 chunk 的副本删除。该命令只能由管理员在控制节点上执行。

## 参数

**chunkId** 是字符串标量或向量，表示 chunk 的 ID。

**nodeAlias** 是一个字符串，表示节点的别名。

## 返回值

无。

## 例子

删除 “node1” 上所有 chunk 的副本。

```dolphindb
chunkIds=exec chunkId from pnodeRun(getChunksMeta) where node="node1"
deleteReplicas(chunkIds,"node1");
```
