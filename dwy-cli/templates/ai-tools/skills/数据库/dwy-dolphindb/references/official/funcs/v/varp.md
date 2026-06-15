---
source_url: https://docs.dolphindb.cn/zh/funcs/v/varp.html
fetched_at: 2026-05-19T09:43:40Z
category: funcs
title: varp
sha1: 085fcd91f15b2c5cc37e7e7dee7c179b00059023
---

# varp

## 语法

`varp(X)`

## 详情

若 *X* 为向量，返回 *X* 的总体方差。

若 *X* 为矩阵，计算每列的总体方差，返回一个向量。

若 *X* 为表，计算每列的总体方差，返回一个表。

与所有其它聚合函数一致，计算时忽略 NULL 值。

## 参数

**X** 可以是向量、矩阵或表。

## 返回值

DOUBLE 类型标量/向量/表。

## 例子

```dolphindb
varp(1 1 1);
// output
0
varp(1 2 3);
// output
0.666667

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
varp(m);
// output
[8,18]
```

相关函数： [cumvarp](../c/cumvarp.html)
