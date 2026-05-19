---
source_url: https://docs.dolphindb.cn/zh/funcs/l/listStreamingSQLTables.html
fetched_at: 2026-05-19T09:29:49Z
category: funcs
title: listStreamingSQLTables
sha1: bea84d8bf45cbea3fc1c35a2f3d067bc5f32d550
---

# listStreamingSQLTables

首发版本：3.00.4

## 语法

`listStreamingSQLTables()`

## 详情

列出当前用户已通过 `declareStreamingSQLTable` 声明的所有流式 SQL 表。

如果调用者是管理员（admin），则会返回系统中所有用户声明的流式 SQL 表。

## 返回值

一张表，包含如下字段：表名（tableName）、是否共享（shared）、声明用户（users）。

## 例子

```dolphindb
t=table(1..10 as id,rand(100,10) as val)
share t as st
declareStreamingSQLTable(st)

listStreamingSQLTables()
```

| tableName | shared | users |
| --- | --- | --- |
| st | true | admin |

**相关函数：**[declareStreamingSQLTable](../d/declareStreamingSQLTable.html)
