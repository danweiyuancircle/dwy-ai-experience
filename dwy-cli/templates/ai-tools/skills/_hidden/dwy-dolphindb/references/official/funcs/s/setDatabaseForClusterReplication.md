---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setDatabaseForClusterReplication.html
fetched_at: 2026-05-19T09:38:30Z
category: funcs
title: setDatabaseForClusterReplication
sha1: e2cb18dc6a98a0d3bd2617f9ffd2fd5010bf5639
---

# setDatabaseForClusterReplication

## 语法

`setDatabaseForClusterReplication(dbHandle, option)`

## 详情

开启/关闭分布式数据库的集群间的异步复制。该函数只能由管理员在主集群的数据节点调用。

相关函数：[getDatabaseClusterReplicationStatus](../g/getDatabaseClusterReplicationStatus.html)

## 参数

`dbHandle`：一个分布式数据库句柄。

`option`：布尔值，表示开启（true）/关闭（false）指定数据库的异步复制，默认为 false。
