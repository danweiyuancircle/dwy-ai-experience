---
source_url: https://docs.dolphindb.cn/zh/funcs/s/share.html
fetched_at: 2026-05-19T09:39:15Z
category: funcs
title: share
sha1: 26e3641e69beae9c5aa7f826d17805223c76935b
---

# share

## 语法

`share(table, sharedName, [database], [dbName],
[partitionColumn], [readonly=false])`

## 详情

如果只有 *table* 和 *sharedName* 两个参数:

- *table*
  是表时，以指定名称在会话中共享表。包括表在内的本地对象在其他会话中不可见的。只有通过共享，它们才能在其他会话中可见。共享表的名称必须与会话中的普通表的名称不同。一般来说，共享的流数据表不支持删除和更新记录，但是
  [table](../t/table.html) 和 [mvccTable](../m/mvccTable.html)
  函数创建的表共享后支持删除和更新记录。所有的共享表都支持插入记录。
- *table* 是引擎时，会对引擎增加写入锁，以实现对引擎的并发写入。

如果使用了5个参数，填充分布式表的碎片，然后以指定名称在会话中共享。分区碎片是以给定列为基础。我们可以使用多个
`share` 语句在多个节点之间保存分区表。

请注意，不可以将同一个流数据表通过修改共享变量名称的方式共享2次及以上。

## 参数

**table** 是要在会话中共享的表或引擎。

**sharedName** 是在会话中共享表的名称，或共享的分布式表的名称。

**database** 是数据库句柄。当该参数是用 [database](../d/database.html) 函数定义时，它需要指定每个分区的名称。

**dbName** 是分布式数据库的名称。

**partitionColumn** 是分布式表的分区列。

**readonly**
是一个布尔值，表示是否将普通/键值/索引内存表共享为一个只读的内存表，以提升读取和查询时的性能。默认值为 false。

## 例子

例 1. 使用 `share` 函数将内存表共享为全局可见的共享表，使得当前节点的所有会话都可以访问该表。这是 DolphinDB
中实现跨会话数据共享的基础方法。

```dolphindb
share(t, `sharedT);
share(t, `quotes, tickDB, `tickDB, `date)
```

例 2. 创建 TSDB 引擎的分布式数据库和表，按日期分区并按时间排序，然后使用 `share` 共享表句柄。

```dolphindb
// 共享通过 loadTable 加载的分布式表
CREATE DATABASE "dfs://valuedb" PARTITIONED BY VALUE(2023.01.01..2023.12.31),engine="TSDB"
CREATE TABLE "dfs://valuedb"."pt"(
    date DATE,
    time TIME,
    sym SYMBOL,
    price DOUBLE
)
PARTITIONED BY date,
sortColumns=`time
share(loadTable("dfs://valuedb", "pt"), `pt)
```

例 3. 创建流数据表作为输入，创建输出表并共享，然后创建响应式状态引擎进行实时计算。使用 `go`
语句确保动态注册的变量能够被后续代码正确引用。

```dolphindb
trades = streamTable(1:0, `time`sym`price, [TIMESTAMP, SYMBOL, DOUBLE])
share(table(100:0, `sym`time`factor1, [SYMBOL, TIMESTAMP, DOUBLE]), `outputTable)
go
engine = createReactiveStateEngine(name="test", metrics=[<time>, <mavg(price, 3)>], dummyTable=trades, outputTable=outputTable, keyColumn=`sym)
```

例 4. 通过 `share` 函数共享响应式状态引擎，为引擎添加写入锁，允许当前节点的所有会话并发地向引擎写入数据。

```dolphindb
// 将引擎 engine 共享
share(engine, "test")

// 第一个自定义函数，向 engine 写入数据
def write1(mutable engine) {
	N = 10
	for (i in 1..500) {
		data = table(take(now(), N) as time, take(`A`B, N) as sym, rand(10.0, N) as price)
		engine.append!(data)
	}
}
// 第二个自定义函数，向 engine 写入数据
def write2(mutable engine) {
	N = 10
	for (i in 1..500) {
		data = table(take(now(), N) as time, take(`C`D, N) as sym, rand(10.0, N) as price)
		engine.append!(data)
	}
}
// 提交作业，使 write1 和 write2 同时向引擎写入数据
submitJob("j1", "j1", write1, engine)
submitJob("j2", "j2", write2, engine)
// 查看输出表中数据行数为 10000，正好是 write1 和 write2 写入的数据量之和。
select count(*) from outputTable 
// output: 10,000
```

相关文档：[undef](../u/undef.html), [取消变量](../../progr/objs/undef_var.html)
