---
source_url: https://docs.dolphindb.cn/zh/funcs/c/clearDSCacheNow.html
fetched_at: 2026-05-19T09:15:18Z
category: funcs
title: clearDSCacheNow
sha1: 5629deb0ac3a6457d75d9459ec440e56b81fa1ea
---

# clearDSCacheNow

## 语法

`clearDSCacheNow(ds)`

## 详情

函数 `clearDSCacheNow` 立即清除数据源和缓存。

## 参数

**ds** 是数据源或数据源列表。

## 返回值

无。

## 例子

```dolphindb
PTNDB_DIR = "/home/db_testing"
dbName = database(PTNDB_DIR + "/NYSETAQByName")
Trades = dbName.loadTable(`Trades)

ds=sqlDS(<select Time,Exchange,Symbol,Trade_Volume as Vol, Trade_Price as Price from Trades>)
ds.cacheDSNow()        // cache the data immediately
ds.clearDSCacheNow()  // clear the cache immediately
```
