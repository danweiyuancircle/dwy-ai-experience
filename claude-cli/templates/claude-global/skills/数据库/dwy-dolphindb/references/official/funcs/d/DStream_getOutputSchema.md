---
source_url: https://docs.dolphindb.cn/zh/funcs/d/DStream_getOutputSchema.html
fetched_at: 2026-05-19T09:19:48Z
category: funcs
title: DStream::getOutputSchema
sha1: 475aee0925448f456cc5e099d48fa2055e13ce49
---

# DStream::getOutputSchema

首发版本：3.00.3

## 语法

`DStream::getOutputSchema()`

## 详情

返回当前 DStream 对象的表结构。

## 参数

无

## 例子

```dolphindb
aggGraph = createStreamGraph("aggregation")
engine = aggGraph.source("trade", `time`sym`price, [TIMESTAMP, SYMBOL, FLOAT])
	.timeSeriesEngine(windowSize=60, step=60, metrics=[<sum(price)>], 
timeColumn="time", keyColumn="sym")
engine.getOutputSchema()

/* output:
time sym sum_price
---- --- ---------
*/
```
