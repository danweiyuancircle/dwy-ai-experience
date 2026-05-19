---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getTablesOfAllClusters.html
fetched_at: 2026-05-19T09:26:23Z
category: funcs
title: getTablesOfAllClusters
sha1: 922edcb3b8f754ca6ad1a7cf90950b8a4c9e11e1
---

# getTablesOfAllClusters

首发版本：3.00.3

## 语法

`getTablesOfAllClusters()`

## 详情

与 `getClusterDFSTables` 函数类似，但此函数能够获取当前用户在多个集群中拥有访问权限的所有表。

## 参数

无

## 返回值

字符串向量。

## 例子

```dolphindb
getTablesOfAllClusters()
// Output:   ["dfs://testDB/pt1", "trading.schema.pt@cluster3"]
```
