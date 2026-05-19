---
source_url: https://docs.dolphindb.cn/zh/funcs/w/warmupcomputenodecache.html
fetched_at: 2026-05-19T09:43:45Z
category: funcs
title: warmupComputeNodeCache
sha1: a32798a0d1452d13d2bc6de7ca369866b0ab5e81
---

# warmupComputeNodeCache

首发版本：3.00.3

## 语法

`warmupComputeNodeCache(sqlObj, [parallelism])`

## 详情

创建数据预热任务，将指定数据缓存至计算组。

## 参数

**sqlObj** SQL 元代码，表示预热的数据。

**parallelism** 可选参数，正整数，表示分配给该任务的线程数上限。

## 返回值

任务的 jobId。

## 例子

```dolphindb
warmupComputeNodeCache(sqlObj=<select * from loadTable("dfs://test","pt") where date>=2025.04.01>, parallelism=3)
```
