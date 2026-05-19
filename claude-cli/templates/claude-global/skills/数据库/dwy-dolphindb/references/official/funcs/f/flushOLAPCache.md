---
source_url: https://docs.dolphindb.cn/zh/funcs/f/flushOLAPCache.html
fetched_at: 2026-05-19T09:21:53Z
category: funcs
title: flushOLAPCache
sha1: f82d6105eadbe88d8fc0fafc72ed9c4bd463d6d2
---

# flushOLAPCache

## 语法

`flushOLAPCache()`

## 详情

将 OLAP 引擎缓冲区里已经完成的事务强制写入数据库。请注意，使用该函数前，需配置
*OLAPCacheEngineSize* 和 *dataSync* = 1。

## 参数

无

## 返回值

无
