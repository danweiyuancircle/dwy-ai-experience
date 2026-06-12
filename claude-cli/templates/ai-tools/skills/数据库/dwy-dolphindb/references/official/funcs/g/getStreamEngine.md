---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getStreamEngine.html
fetched_at: 2026-05-19T09:25:59Z
category: funcs
title: getStreamEngine
sha1: e89f3d82365507f3d2f69c4f269ee4d28f58927e
---

# getStreamEngine

## 语法

`getStreamEngine(name)`

## 详情

返回流数据引擎的句柄，可以作为 [subscribeTable](../s/subscribeTable.html) 函数的
*handler* 参数。

## 参数

**name** 是一个字符串，表示流数据引擎的名称。它可以包含字母，数字和下划线，但必须以字母开头。

## 返回值

一个流数据引擎对象。

## 例子

```dolphindb
share streamTable(1000:0, `time`sym`qty, [TIMESTAMP, SYMBOL, INT]) as trades
outputTable = table(10000:0, `time`sym`sumQty, [TIMESTAMP, SYMBOL, INT])
tradesAggregator = createTimeSeriesEngine("StreamAggregatorDemo",3, 3, <[sum(qty)]>, trades, outputTable, `time, false,`sym, 50)
subscribeTable(, "trades", "tradesAggregator", 0, append!{tradesAggregator}, true)

def writeData(n){
   timev = 2018.10.08T01:01:01.001 + timestamp(1..n)
   symv =take(`A`B, n)
   qtyv = take(1, n)
   insert into trades values(timev, symv, qtyv)
}

writeData(6);
h = getStreamEngine("StreamAggregatorDemo")
```
