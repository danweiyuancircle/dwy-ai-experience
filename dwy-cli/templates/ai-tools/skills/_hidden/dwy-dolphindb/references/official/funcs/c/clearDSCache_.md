---
source_url: https://docs.dolphindb.cn/zh/funcs/c/clearDSCache_.html
fetched_at: 2026-05-19T09:15:17Z
category: funcs
title: clearDSCache!
sha1: 1805c0060f7d565ddb9b0efd14072d6ec6be40dc
---

# clearDSCache!

## 语法

`clearDSCache!(ds)`

## 详情

`clearDSCache!` 函数指示系统在下次执行数据源之后清除缓存。

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
ds.cacheDS!()        // cache the data
ds.clearDSCache!()  // clear the cache
```
