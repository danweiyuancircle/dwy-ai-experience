---
source_url: https://docs.dolphindb.cn/zh/funcs/u/unsubscribeStreamingSQL.html
fetched_at: 2026-05-19T09:43:14Z
category: funcs
title: unsubscribeStreamingSQL
sha1: 9ffdf3bb0b0bcee81557d8d076d5c62828c7ed8b
---

# unsubscribeStreamingSQL

首发版本：3.00.4

## 语法

`unsubscribeStreamingSQL([server], queryId)`

## 详情

取消订阅指定的流式 SQL 查询结果。取消订阅后，订阅端的实时结果表将停止更新。

## 参数

**server** 可选参数，字符串标量，表示运行流式 SQL 查询的节点（即注册该查询的服务器）的别名或远程连接句柄。如果未指定或者为空字符串，表示流式 SQL
查询所在的服务器是本地实例。

**queryId** 字符串标量，表示要取消订阅的流式 SQL 查询 ID。

## 返回值

无。

## 例子

```dolphindb
t=table(1..10 as id,rand(100,10) as val)
share t as st
declareStreamingSQLTable(st)
registerStreamingSQL("select avg(val) from st","sql_avg") 

subscribeStreamingSQL(queryId="sql_avg")
// output: 52.1

unsubscribeStreamingSQL(queryId="sql_avg")
```

**相关函数：**[declareStreamingSQLTable](../d/declareStreamingSQLTable.html), [registerStreamingSQL](../r/registerStreamingSQL.html), [subscribeStreamingSQL](../s/subscribeStreamingSQL.html)
