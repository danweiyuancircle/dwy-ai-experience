---
source_url: https://docs.dolphindb.cn/zh/funcs/r/revokeStreamingSQLTable.html
fetched_at: 2026-05-19T09:36:29Z
category: funcs
title: revokeStreamingSQLTable
sha1: 5b0d26cc95804bedfbfbdf46297aa4fc033544f8
---

# revokeStreamingSQLTable

首发版本：3.00.4

## 语法

`revokeStreamingSQLTable(tableName)`

## 详情

注销一个通过 `declareStreamingSQLTable` 声明的流式 SQL 表。

- 只能取消当前用户自己声明的表。
- 注销前，必须先取消在该表上已注册的所有流式 SQL 查询。
- 注销操作仅移除表的流式 SQL 功能，不会删除表本身或表中的数据。

## 参数

**tableName** 字符串标量，表示已声明的流式 SQL 表的名称。

## 例子

```dolphindb
t=table(1..10 as id,rand(100,10) as val)
share t as st
declareStreamingSQLTable(st)
registerStreamingSQL("select avg(val) from st","sql_avg")

// 取消已注册的流式 SQL 查询
revokeStreamingSQL("sql_avg")

// 注销流式 SQL 表
revokeStreamingSQLTable(`st)
```

**相关函数：**[declareStreamingSQLTable](../d/declareStreamingSQLTable.html), [listStreamingSQLTables](../l/listStreamingSQLTables.html), [registerStreamingSQL](registerStreamingSQL.html), [revokeStreamingSQL](revokeStreamingSQL.html)
