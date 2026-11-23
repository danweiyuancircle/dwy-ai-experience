---
source_url: https://docs.dolphindb.cn/zh/progr/data_mani/sort_null.html
fetched_at: 2026-05-19T09:02:26Z
category: progr
title: 空值排序
sha1: 5b1cd42ca6e081db4bf6095d674206df51345f51
---

# 空值排序

一个特定类型的空值被定义为相应数据类型的最小值，因此按升序排序时空值总排在最前面。

```dolphindb
x = 1 2 NULL NULL 3;
x;
// output
[1,2,,,3]

sort!(x);
// output
[,,1,2,3]
// 对 x 进行升序排序，空值将位于开头处。

sort!(x,false);
// output
[3,2,1,,]
// 对 x 进行降序排序，空值将位于末尾处。
```

在导入外部数据或进行计算过程中，产生的负无穷（-inf）值比空值小。

```dolphindb
//使用 float 函数生成一个 -inf 值，并与 NULL 进行比较
-float("inf")<NULL
//output
true
```

在 SQL 语句中，可以显式地通过 `NULLS FIRST` 或 `NULLS
LAST`指定空值的排序方式。

```dolphindb
sort(3 2 NULL 5, true)
// output: NULL 2 3 5

sort(3 2 NULL 5, false)
// output: 5 3 2 NULL

t = table(1 2 3 4 as id, 3 2 NULL 5 as value)
select * from t order by value asc nulls last
```

| id | value |
| --- | --- |
| 2 | 2 |
| 1 | 3 |
| 4 | 5 |
| 3 |  |

```dolphindb
select * from t order by value desc nulls first
```

| id | value |
| --- | --- |
| 3 |  |
| 4 | 5 |
| 1 | 3 |
| 2 | 2 |
