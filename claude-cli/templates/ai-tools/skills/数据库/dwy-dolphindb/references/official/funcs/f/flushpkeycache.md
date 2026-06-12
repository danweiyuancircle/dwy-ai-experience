---
source_url: https://docs.dolphindb.cn/zh/funcs/f/flushpkeycache.html
fetched_at: 2026-05-19T09:21:54Z
category: funcs
title: flushPKEYCache
sha1: 18451c512d3b9ffa444b4f38059294cf3d01b8ff
---

# flushPKEYCache

## 语法

`flushPKEYCache()`

## 详情

将 PKEY 引擎 CacheEngine 里的数据强制写入磁盘，包括各分区上已经完成的事务的数据和长时间未使用的 Symbol
Base。

## 参数

无

## 返回值

无

## 例子

```dolphindb
flushPKEYCache()
```
