---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getStreamTableFilterColumn.html
fetched_at: 2026-05-19T09:26:14Z
category: funcs
title: getStreamTableFilterColumn
sha1: f2c7d92b3569ae507c904f474e9e9706e6bb7d0f
---

# getStreamTableFilterColumn

## 语法

`getStreamTableFilterColumn(streamTable)`

## 详情

返回由函数 [setStreamTableFilterColumn](../s/setStreamTableFilterColumn.html) 指定的流数据表中过滤列的名称。

## 参数

**streamTable** 是流数据表。

## 返回值

字符串标量。

## 例子

```dolphindb
share streamTable(10000:0,`time`symbol`price, [TIMESTAMP,SYMBOL,INT]) as trades
setStreamTableFilterColumn(trades, `symbol)
trades_1=table(10000:0,`time`symbol`price, [TIMESTAMP,SYMBOL,INT])
filter=symbol(`IBM`GOOG)
subscribeTable(tableName=`trades, actionName=`trades_1, handler=append!{trades_1}, msgAsTable=true, filter=filter);

n=100
time=take(2018.01.01T09:30:00.000,n)
symbol=take((`IBM`GOOG`AAPL`C`BABA),n)
price=1..n

t=table(time,symbol,price)
trades.append!(t)

// 获取流数据表trades由setStreamTableFilterColumn函数指定的过滤列名
getStreamTableFilterColumn(trades) ;
// output: symbol
```
