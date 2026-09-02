---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getGroupAccessByCluster.html
fetched_at: 2026-05-19T09:23:48Z
category: funcs
title: getGroupAccessByCluster
sha1: 55e96fa4993d54099882c2cfb3d7ea55248f7438
---

# getGroupAccessByCluster

首发版本：3.00.3

## 语法

`getGroupAccessByCluster(groupIds, clusterName)`

## 详情

查询指定用户组的权限。只能由管理员在 MoM（Master of Master，管理集群）上执行该函数。

## 参数

**groupIds** 字符串标量或向量，表示要查询的用户组名称。

**clusterName** 字符串标量，表示用户组所属的集群名称。

## 返回值

返回一个表， 字段与 `getGroupAccess` 函数的返回结果一致。

## 例子

```dolphindb
getGroupAccessByCluster(["group2"], "MoMSender")  
```

| groupName | users | ACCESS\_READ | ACCESS\_INSERT | ACCESS\_UPDATE | ACCESS\_DELETE | VIEW\_EXEC | SCRIPT\_EXEC | TEST\_EXEC | DBOBJ\_CREATE | ... |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| group2 | user2 | none | allow | none | none | none | none | none | none | ... |

相关函数：[getGroupAccess](getGroupAccess.html)
