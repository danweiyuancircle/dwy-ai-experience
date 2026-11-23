---
source_url: https://docs.dolphindb.cn/zh/funcs/s/std.html
fetched_at: 2026-05-19T09:40:06Z
category: funcs
title: std
sha1: 27a1b2331515b2bf57206e503e86cd294d3cef4a
---

# std

## 语法

`std(X)`

## 详情

若 *X* 为向量，返回 *X* 的标准差。

若 *X* 为矩阵，计算每列的标准差，返回一个向量。

若 *X* 为表，计算每列的标准差，返回一个表。

与所有其它聚合函数一致，计算时忽略 NULL 值。

注：

该函数返回无偏差样本标准差（unbiased sample standard
deviation），而不是总体标准差。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

一个标量、向量或表。

## 例子

```dolphindb
std(1 2 3);
// output
1

m=matrix(1 3 5 7 9, 1 4 7 10 13);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 1 |
| 3 | 4 |
| 5 | 7 |
| 7 | 10 |
| 9 | 13 |

```dolphindb
std(m);
// output
[3.162277660168379,4.743416490252569]
```

相关函数：[std](std.html), [cumstd](../c/cumstd.html)
