---
source_url: https://docs.dolphindb.cn/zh/funcs/c/clearalltsdbsymbolbasecache.html
fetched_at: 2026-05-19T09:15:12Z
category: funcs
title: clearAllTSDBSymbolBaseCache
sha1: bb86bb0da88fd1fcf9e254586c1e6949c0a996d1
---

# clearAllTSDBSymbolBaseCache

## 语法

`clearAllTSDBSymbolBaseCache()`

## 详情

清除缓存中所有未被使用的 symbolBase。其中，未被使用的 symbolBase 是指其对应分区的数据不在 Cache Engine
中，也不在执行的任何事务中。

## 参数

无。

## 返回值

无。

## 例子

```dolphindb
clearAllTSDBSymbolBaseCache();
```
