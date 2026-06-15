---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getChunkPath.html
fetched_at: 2026-05-19T09:22:59Z
category: funcs
title: getChunkPath
sha1: 3792209ee57d29ab7ce25138943f0ce12787fa71
---

# getChunkPath

## 语法

`getChunkPath(ds)`

## 详情

返回指定数据源代表数据块的路径。

## 参数

**ds** 是一个或多个数据源。

## 返回值

字符串向量。

## 例子

```dolphindb
if(existsDatabase("dfs://valuedb")){
  dropDatabase("dfs://valuedb")
}

db=database("dfs://valuedb", VALUE, 1..10)
n=1000000
t=table(rand(1..10, n) as id, rand(100.0, n) as val)
pt=db.createPartitionedTable(t, `pt, `id).append!(t);
ds=sqlDS(<select * from pt where id in 1..3>)
getChunkPath(ds);

// output
["/valuedb/1/p","/valuedb/2/p","/valuedb/3/p"]
```
