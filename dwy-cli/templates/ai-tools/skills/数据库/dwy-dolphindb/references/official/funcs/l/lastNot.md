---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lastNot.html
fetched_at: 2026-05-19T09:29:27Z
category: funcs
title: lastNot
sha1: 1d7fdc30d04e5e36a9012add88a7da144523b5f0
---

# lastNot

## 语法

`lastNot(X, [k])`

## 详情

若 *X* 是向量：

- 如果没有指定 *k*，返回 *X* 中最后一个不为 NULL 的元素。
- 如果指定 *k*，返回 *X* 中最后一个不为 *k* 或 NULL 的元素。

若 *X* 是矩阵或表，在每列内进行上述计算，返回一个向量。

`lastNot` 函数也支持查询分布式表和分区表。

## 参数

**X** 是向量、矩阵或表。

**k** 是标量。它是一个可选参数。

## 返回值

- 如果 *X* 是一个向量，返回一个标量。
- 如果 *X* 是一个矩阵，返回一个向量。
- 如果 *X* 是一张表，返回一张表。

## 例子

```dolphindb
lastNot(1 6 0 0 0, 0);
```

输出返回：6

```dolphindb
lastNot(1 6 0 0 0 2 3 0 NULL, 0);
```

输出返回：3

```dolphindb
lastNot(1 6 0 0 0 2 3 0 NULL);
```

输出返回：0

```dolphindb
t=table(1 1 1 1 1 2 2 2 2 2 as id, 1 2 0 0 0 3 NULL NULL 0 0 as x);
t;
```

输出返回：

表 1.

| id | x |
| --- | --- |
| 1 | 1 |
| 1 | 2 |
| 1 | 0 |
| 1 | 0 |
| 1 | 0 |
| 2 | 3 |
| 2 |  |
| 2 |  |
| 2 | 0 |
| 2 | 0 |

```dolphindb
select lastNot(x, 0) from t group by id;
```

输出返回：

| id | lastNot\_x |
| --- | --- |
| 1 | 2 |
| 2 | 3 |

```dolphindb
m=matrix(2 NULL 1 0 NULL, NULL 2 NULL 6 0);
m;
```

输出返回：

| #0 | #1 |
| --- | --- |
| 2 | 2 |
| 1 |  |
| 0 | 6 0 |

```dolphindb
lastNot(m, 0);
```

输出返回：[1,6]
