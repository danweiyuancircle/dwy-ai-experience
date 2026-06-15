---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getTableAccessByCluster.html
fetched_at: 2026-05-19T09:26:22Z
category: funcs
title: getTableAccessByCluster
sha1: 370ec334e6b4fdd2f3bc00fed5bcd3577ee55cee
---

# getTableAccessByCluster

首发版本：3.00.3

## 语法

`getTableAccessByCluster(table)`

## 详情

获取指定表的所有用户权限。只能由管理员在 MoM（Master of Master，管理集群）上执行该函数。

## 参数

**table** 字符串标量，表示一个表，形如：`{catalog}.{schema}.{pt}@{cluster}`。

## 返回值

一个表，字段与 `getTableAccess` 函数的返回结果一致。

## 例子

```dolphindb
getTableAccessByCluster("catalog1.schema1.dt@MoMSender")
```

| name | type | TABLE\_READ | TABLE\_INSERT | TABLE\_UPDATE | TABLE\_DELETE |
| --- | --- | --- | --- | --- | --- |
| admin | user | ALLOW | ALLOW | ALLOW | ALLOW |

相关函数：[getTableAccess](gettableaccess.html)
