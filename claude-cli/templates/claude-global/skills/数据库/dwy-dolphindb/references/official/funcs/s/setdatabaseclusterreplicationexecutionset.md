---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setdatabaseclusterreplicationexecutionset.html
fetched_at: 2026-05-19T09:38:31Z
category: funcs
title: setDatabaseClusterReplicationExecutionSet
sha1: 800fcac7872559874831c6de26112b7a84918679
---

# setDatabaseClusterReplicationExecutionSet

## 语法

`setDatabaseClusterReplicationExecutionSet(dbHandle,
executionSet)`

## 详情

为一个数据库设置异步复制任务的执行集。不同执行集的任务彼此隔离，互不影响。此函数只能由管理员在主集群的数据节点上对开启了异步复制的数据库执行。

## 参数

**dbHandle** 数据库句柄，代表要设置执行集的数据库。

**executionSet** 整型标量，只能是 0 或 1，代表执行集。数据库启用异步复制后，默认的执行集为 0。

## 例子

```dolphindb
setDatabaseClusterReplicationExecutionSet(dbHandle=database("dfs://test"), executionSet=1)
```
