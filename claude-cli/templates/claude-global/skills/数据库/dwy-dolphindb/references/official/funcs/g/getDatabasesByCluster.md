---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getDatabasesByCluster.html
fetched_at: 2026-05-19T09:23:29Z
category: funcs
title: getDatabasesByCluster
sha1: 653b37c5ea5dd4f239534603af0419896cfb81de
---

# getDatabasesByCluster

首发版本：3.00.3

## 语法

`getDatabasesByCluster(clusterName)`

## 详情

获取集群下所有数据库。只能由管理员在 MoM（Master of Master，管理集群）上执行该函数。

## 参数

**clusterName** 字符串标量，表示要查询的集群名称。

## 返回值

字符串向量。

## 例子

```dolphindb
getDatabasesByCluster("MoMSender")

// Output:   ["dfs://db2","dfs://db1"]
```
