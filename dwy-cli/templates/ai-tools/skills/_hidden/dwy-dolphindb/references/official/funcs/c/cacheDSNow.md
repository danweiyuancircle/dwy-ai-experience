---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cacheDSNow.html
fetched_at: 2026-05-19T09:14:24Z
category: funcs
title: cacheDSNow
sha1: b5730e6d1b7bac627a9c48cd2b6563bdb10582e0
---

# cacheDSNow

## 语法

`cacheDSNow(ds)`

## 详情

函数 `cacheDSNow` 立即执行并缓存数据源和缓存行的总数。

## 参数

**ds** 是数据源或数据源列表。

## 返回值

INT 类型标量。

## 例子

```dolphindb
PTNDB_DIR = "/home/db_testing"
dbName = database(PTNDB_DIR + "/NYSETAQByName")
Trades = dbName.loadTable(`Trades)

ds=sqlDS(<select Time,Exchange,Symbol,Trade_Volume as Vol, Trade_Price as Price from Trades>)
ds.cacheDSNow()        # cache the data immediately
ds.clearDSCacheNow()  # clear the cache immediately
```
