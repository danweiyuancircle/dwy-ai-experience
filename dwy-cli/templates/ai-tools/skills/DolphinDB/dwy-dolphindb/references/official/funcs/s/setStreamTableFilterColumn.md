---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setStreamTableFilterColumn.html
fetched_at: 2026-05-19T09:39:04Z
category: funcs
title: setStreamTableFilterColumn
sha1: 534abf29056c2d8e994ce4bf852b08b9606181c7
---

# setStreamTableFilterColumn

## 语法

`setStreamTableFilterColumn(streamTable, columnName)`

## 详情

指定流数据表的过滤列。该函数需要配合 [subscribeTable](subscribeTable.html) 函数的 *filter* 参数一起使用。*filter*
是一个向量，*streamTable* 的 *columnName* 列在 *filter* 中的数据才会发布到订阅端，不在
*filter* 中的数据不会发布。一个流数据表只能指定一个过滤列。

## 参数

**streamTable** 是流数据表。

**columnName** 是一个字符串。

## 例子

下例中，指定了流数据表 trades 的 symbol 列为过滤列，同一节点上的表 trades\_slave 订阅流数据表
trades 时把 filter 设置为 ["IBM", "GOOG"]，即流数据表 trades 的 symbol 为 "IBM" 或 "GOOG"
时才会发布到订阅端。

```dolphindb
share streamTable(10000:0,`time`symbol`price, [TIMESTAMP,SYMBOL,INT]) as trades
setStreamTableFilterColumn(trades, `symbol)
trades_1=table(10000:0,`time`symbol`price, [TIMESTAMP,SYMBOL,INT])

filter=symbol(`IBM`GOOG)

subscribeTable(tableName=`trades, actionName=`trades_1, handler=append!{trades_1}, msgAsTable=true, filter=filter);
```
