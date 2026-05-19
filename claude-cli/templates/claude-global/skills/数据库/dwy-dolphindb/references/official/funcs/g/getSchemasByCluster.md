---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getSchemasByCluster.html
fetched_at: 2026-05-19T09:25:48Z
category: funcs
title: getSchemasByCluster
sha1: 2cf22b3f2fa1251209ba4dfed85315cd924765e1
---

# getSchemasByCluster

首发版本：3.00.3

## 语法

`getSchemasByCluster(clusterName, catalogName)`

## 详情

查询集群下指定 catalog 的所有的 schema。只能由管理员在 MoM（Master of Master，管理集群）上执行该函数。

## 参数

**clusterName** 字符串标量，表示要查询的集群名称。

**catalogName** 字符串标量，表示要查询的 catalog 的名称。

## 返回值

一个表，包含以下字段：

- schema：字符串类型，schema 的名称。
- dbUrl：字符串类型，数据库路径。

## 例子

```dolphindb
// MoMSender 的数据节点：
database(directory="dfs://db1", partitionType=RANGE, partitionScheme=0 5 10)
database(directory="dfs://db2", partitionType=RANGE, partitionScheme=0 5 10)
createSchema("catalog1", "dfs://db1", "schema1")
createSchema("catalog1", "dfs://db2", "schema2")

// MOM 节点：
getSchemasByCluster("MoMSender", "catalog1")
```

| schema | dbUrl |
| --- | --- |
| schema1 | dfs://db1 |
| schema2 | dfs://db2 |
