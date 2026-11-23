---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getGroupListOfAllClusters.html
fetched_at: 2026-05-19T09:23:50Z
category: funcs
title: getGroupListOfAllClusters
sha1: 63e826b2a5dcc06c010b73e7569c6a77fb126a4f
---

# getGroupListOfAllClusters

首发版本：3.00.3

## 语法

`getGroupListOfAllClusters()`

## 详情

查询多集群系统中所有集群的用户组信息。只能由管理员在 MoM（Master of Master，管理集群）上执行该函数。

## 参数

无

## 返回值

返回一个字典，其中：

- key：集群名称。
- value：用户组名称列表。

## 例子

```dolphindb
getGroupListOfAllClusters()
      
/* Output:
masterOfMaster->["group1"]
MoMSender->["group2"]  
*/  
```
