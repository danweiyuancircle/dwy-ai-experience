---
source_url: https://docs.dolphindb.cn/zh/funcs/e/existsDatabase.html
fetched_at: 2026-05-19T09:21:20Z
category: funcs
title: existsDatabase
sha1: 862e7eb4b82750e890e1a28da3873e02488bbf4a
---

# existsDatabase

## 语法

`existsDatabase(dbUrl)`

## 详情

检查指定数据库是否存在。

## 参数

**dbUrl** 是一个字符串，表示数据库的路径。

## 返回值

布尔类型标量。 false 和 true 分别表示指定的数据库不存在、存在。

## 例子

检查分布式数据库是否存在：

```dolphindb
n=1000000
ID=rand(10, n)
dates=2017.08.07..2017.08.11
date=rand(dates, n)
x=rand(10.0, n)
t=table(ID, date, x)

db = database("dfs://valueDB", VALUE, 2017.08.07..2017.08.11)
pt = db.createPartitionedTable(t, `pt, `date);
pt.append!(t);

existsDatabase("dfs://valueDB");
```

输出返回：true

```dolphindb
existsDatabase("dfs://valueDB/20170807");
```

输出返回：false
