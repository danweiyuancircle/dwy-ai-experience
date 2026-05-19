---
source_url: https://docs.dolphindb.cn/zh/funcs/c/clearCachedDatabase.html
fetched_at: 2026-05-19T09:15:13Z
category: funcs
title: clearCachedDatabase
sha1: 177d68b27d98bfec8a25f9f2d18cb974cfc467f0
---

# clearCachedDatabase

## 语法

`clearCachedDatabase(dbUrl, [tableName])`

## 详情

清理从数据库加载到内存的数据表的缓存。通过函数 [getSessionMemoryStat](../../g/getSessionMemoryStat.dita) 可以查看系统中的不同缓存的占用情况。

## 参数

**dbUrl** 一个字符串，表示分布式数据库的路径。

**tableName** 一个字符串，表示数据表的表名，可以是维度表或分布式表。

## 返回值

无。
