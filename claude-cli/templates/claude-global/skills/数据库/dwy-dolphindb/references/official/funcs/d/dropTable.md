---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropTable.html
fetched_at: 2026-05-19T09:19:36Z
category: funcs
title: dropTable
sha1: b391ddc12b9a6db8a8c287efa25dec37f2df93f6
---

# dropTable

## 语法

`dropTable(dbHandle, tableName)`

## 详情

删除指定的表。该命令只能在数据节点/计算节点上执行，不能在控制节点和代理节点上执行。

## 参数

**dbHandle** 是数据库句柄。

**tableName** 是一个字符串，表示表名。

## 返回值

无。

## 例子

```dolphindb
n=1000000
ID=rand(10, n)
x=rand(1.0, n)
t=table(ID, x)
db=database("dfs://rangedb", RANGE,  0 5 10)
pt = db.createPartitionedTable(t, `pt, `ID)
pt.append!(t)

dropTable(db,`pt);
```
