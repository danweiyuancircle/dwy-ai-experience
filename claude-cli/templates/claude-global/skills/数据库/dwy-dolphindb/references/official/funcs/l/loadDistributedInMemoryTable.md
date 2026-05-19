---
source_url: https://docs.dolphindb.cn/zh/funcs/l/loadDistributedInMemoryTable.html
fetched_at: 2026-05-19T09:29:54Z
category: funcs
title: loadDistributedInMemoryTable
sha1: 892f71ec3c4fda0159afb5fac18bf8ef89c60f96
---

# loadDistributedInMemoryTable

## 语法

`loadDistributedInMemoryTable(tableName)`

## 详情

返回分布式共享内存表的句柄。该函数只能在数据节点/计算节点上执行。

## 参数

**tableName** 字符串标量，表示分布式共享内存表的名称。

## 返回值

一个分布式共享内存表的句柄。

## 例子

```dolphindb
pt = createDistributedInMemoryTable(`dt, `time`id`value, `DATETIME`INT`LONG, HASH, [INT, 2],`id)
time = take(2021.08.20 00:00:00..2021.08.30 00:00:00, 40);
id = 0..39;
value = rand(100, 40);
tmp = table(time, id, value);

pt = loadDistributedInMemoryTable(`dt)
pt.append!(tmp);
select * from pt;
```

相关函数：[dropDistributedInMemoryTable](../d/dropDistributedInMemoryTable.html), [createDistributedInMemoryTable](../c/createDistributedInMemoryTable.html)
