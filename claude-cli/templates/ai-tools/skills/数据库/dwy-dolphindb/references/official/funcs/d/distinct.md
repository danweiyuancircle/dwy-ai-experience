---
source_url: https://docs.dolphindb.cn/zh/funcs/d/distinct.html
fetched_at: 2026-05-19T09:19:08Z
category: funcs
title: distinct
sha1: 6f7802d5738a5bd9c631a436f45d8024499dc463
---

# distinct

## 语法

`distinct(X)`

## 详情

去除 *X* 中的重复元素，返回唯一值。3.00.4 版本起，返回结果的顺序与输入顺序保持一致。

## 参数

**X** 是一个向量或数组向量类型。

## 返回值

DOUBLE 类型向量。

## 例子

```dolphindb
distinct(4 5 5 2 3)
// output: [4,5,2,3]

a = array(INT[], 0, 10).append!([1 2 3,  4 5, 6 7 8, 9 10])
distinct(a)
// output: [1,2,3,4,5,6,7,8,9,10]

t=table(3 1 2 2 3 as x);
select distinct x from t;
```

| distinct\_x |
| --- |
| 3 |
| 1 |
| 2 |

```dolphindb
select sort(distinct(x)) as x from t;
```

| x |
| --- |
| 1 |
| 2 |
| 3 |

函数 `distinct` 返回一个向量，而函数 [`set`](../s/set.html) 返回一个集合。

```dolphindb
x=set(4 5 5 2 3);
x;
// output
set(3,2,5,4)
x.intersection(set(2 5));
// output
set(2,5)
```

在内存表或分布式表中，`distinct` 函数可以和
`group by` 配合使用，每个分组的结果为一个数组向量。

```dolphindb
dbName = "dfs://testdb"
if(existsDatabase(dbName)){
   dropDatabase(dbName)
}

db=database("dfs://testdb", VALUE, 2012.01.11..2012.01.29)

n=100
t=table(take(2012.01.11..2012.01.29, n) as date, symbol(take("A"+string(21..60), n)) as sym, take(100, n) as val)

pt=db.createPartitionedTable(t, `pt, `date).append!(t)
result=select distinct(date) from pt group by sym
select sym, distinct_date from result where sym=`A21
```

| sym | distinct\_date |
| --- | --- |
| A21 | [2012.01.15,2012.01.13,2012.01.11] |
