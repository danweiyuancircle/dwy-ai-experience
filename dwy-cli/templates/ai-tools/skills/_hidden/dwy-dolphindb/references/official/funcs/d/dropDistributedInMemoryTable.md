---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropDistributedInMemoryTable.html
fetched_at: 2026-05-19T09:19:21Z
category: funcs
title: dropDistributedInMemoryTable
sha1: 7ade7de2f4fd83ba631dfbcffd471932e1bf9592
---

# dropDistributedInMemoryTable

## 语法

`dropDistributedInMemoryTable(tableName)`

## 详情

删除指定的表。该命令只能在数据节点/计算节点上执行。

## 参数

**tableName** 字符串标量，表示分布式共享内存表的名称。

## 返回值

无。

## 例子

```dolphindb
pt = createDistributedInMemoryTable(`dt, `time`id`value, `DATETIME`INT`LONG, HASH, [INT, 2],`id)
time = take(2021.08.20 00:00:00..2021.08.30 00:00:00, 40);
id = 0..39;
value = rand(100, 40);
tmp = table(time, id, value);

pt = loadDistributedInMemoryTable(`dt)
pt.append!(tmp);
dropDistributedInMemoryTable(`dt)
```

相关函数：[loadDistributedInMemoryTable](../l/loadDistributedInMemoryTable.html), [createDistributedInMemoryTable](../c/createDistributedInMemoryTable.html)
