---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getUserListOfAllClusters.html
fetched_at: 2026-05-19T09:26:50Z
category: funcs
title: getUserListOfAllClusters
sha1: 7f13c46bcd7baf41bc99ca47443bc8af8a7e3c4b
---

# getUserListOfAllClusters

首发版本：3.00.3

## 语法

`getUserListOfAllClusters()`

## 详情

查询多集群管理系统中所有集群的用户信息。只能由管理员在 MoM（Master of Master，管理集群）上执行该函数。

## 参数

无

## 返回值

一个字典（dictionary），其中：

- key：集群名称。
- value：该集群下的用户名称列表。

## 例子

```dolphindb
getUserListOfAllClusters()
      
/* Output:
masterOfMaster->["user1","user2","admin"]
MoMSender->["admin","user2"]  
*/   
```
