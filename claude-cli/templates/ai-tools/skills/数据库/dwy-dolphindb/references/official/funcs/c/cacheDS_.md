---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cacheDS_.html
fetched_at: 2026-05-19T09:14:22Z
category: funcs
title: cacheDS!
sha1: 2dfc22628f097b7acf0880cdf60db978947c9e22
---

# cacheDS!

## 语法

`cacheDS!(ds)`

## 详情

函数 `cacheDS!` 会在下次执行，并缓存数据。

## 参数

**ds** 是数据源或数据源列表。

## 返回值

返回 true 或 false 表示此操作成功或失败。

## 例子

```dolphindb
PTNDB_DIR = "/home/db_testing"
dbName = database(PTNDB_DIR + "/NYSETAQByName")
Trades = dbName.loadTable(`Trades)

ds=sqlDS(<select Time,Exchange,Symbol,Trade_Volume as Vol, Trade_Price as Price from Trades>)
ds.cacheDS!()        // cache the data
ds.clearDSCache!()  // clear the cache
```
