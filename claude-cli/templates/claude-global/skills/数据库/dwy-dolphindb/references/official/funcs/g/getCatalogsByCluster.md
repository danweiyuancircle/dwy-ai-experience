---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getCatalogsByCluster.html
fetched_at: 2026-05-19T09:22:54Z
category: funcs
title: getCatalogsByCluster
sha1: 5273481007a34a2052a66c15699bc41c46530382
---

# getCatalogsByCluster

首发版本：3.00.3

## 语法

`getCatalogsByCluster(clusterName)`

## 详情

查询指定集群所有的数据目录（catalog）。只能由管理员在 MoM（Master of Master，管理集群）上执行该函数。

**返回值：**字符串向量。

## 参数

**clusterName** 字符串标量或向量，表示集群名称。

## 返回值

字符串向量。

## 例子

```dolphindb
// MoMSender 集群：
createCatalog("catalog1")
createCatalog("catalog2")
createCatalog("catalog3")
createCatalog("catalog4")

// MoM 集群：
getCatalogsByCluster("MoMSender")
// Output: ["catalog1","catalog2","catalog3","catalog4"] 
```
