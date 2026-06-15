---
source_url: https://docs.dolphindb.cn/zh/funcs/d/DStream_sync.html
fetched_at: 2026-05-19T09:20:19Z
category: funcs
title: DStream::sync
sha1: a30ba96731bbc5708d1db205560de80c977b6f0b
---

# DStream::sync

首发版本：3.00.3

## 语法

`DStream::sync()`

## 详情

等待所有并行任务完成再进行后续处理（用于汇合并行路径）。

注意：`DStream::parallelize` 和 `DStream::sync`
接口必须同时调用。

## 参数

无

## 返回值

返回一个 DStream 对象。

## 例子

基于 symbol 列拆分 4 个分区，分别执行计算任务：

```dolphindb
use catalog test

g = createStreamGraph("graph")
g.source("trade", `symbol`datetime`price`volume, [SYMBOL, TIMESTAMP,DOUBLE, INT])
  .parallelize("symbol", 4)
  .timeSeriesEngine(60*1000, 60*1000, <[first(price),max(price),min(price),last(price),sum(volume)]>, "datetime", false, "symbol")
  .reactiveStateEngine(<[datetime, first_price, max_price, min_price, last_price, sum_volume, mmax(max_price, 5), mavg(sum_volume, 5)]>, `symbol)
  .sync()
  .sink("output")
g.submit()
```
