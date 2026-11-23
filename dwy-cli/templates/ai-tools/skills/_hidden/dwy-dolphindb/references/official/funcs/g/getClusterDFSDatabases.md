---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getClusterDFSDatabases.html
fetched_at: 2026-05-19T09:23:02Z
category: funcs
title: getClusterDFSDatabases
sha1: 326a0fb3c1365c8510a6bea207fe9b56fdc1b2ce
---

# getClusterDFSDatabases

## 语法

`getClusterDFSDatabases([includeSysDb=true])`

## 详情

该函数由管理员执行时，返回当前集群中的分布式数据库；

由其他用户执行时，返回该用户在集群中拥有以下权限的分布式数据库：DB\_OWNER, DB\_MANAGE, DB\_READ, DB\_INSERT, DB\_UPDATE,
DB\_DELETE, DBOBJ\_CREATE, DBOBJ\_DELETE。

## 参数

**includeSysDb** 可选参数，布尔值，用于控制返回的结果中是否包含系统库，默认值为
true。该参数仅对管理员用户生效。如果是普通用户，即便将 *includeSysDb* 设置为 true 也无法查看系统库。

## 返回值

字符串向量。

## 例子

```dolphindb
getClusterDFSDatabases()

// output: ["dfs://demohash","dfs://myDataYesDB","dfs://testDB"]
```
