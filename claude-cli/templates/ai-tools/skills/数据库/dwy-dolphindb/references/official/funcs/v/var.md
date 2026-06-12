---
source_url: https://docs.dolphindb.cn/zh/funcs/v/var.html
fetched_at: 2026-05-19T09:43:37Z
category: funcs
title: var
sha1: 1eff2666c88f7012b104cfbe0283fbe0b1c047b9
---

# var

## 语法

`var(X)`

## 详情

若 *X* 为向量，返回 *X* 的方差(variance)。

若 *X* 为矩阵，计算每列的方差，返回一个向量。

若 *X* 为表，计算每列的方差，返回一个表。

与所有其它聚合函数一致，计算时忽略 NULL 值。

请注意，返回无偏样本方差（unbiased sample variance），而不是总体方差。

无偏样本方差的公式如下：

s
2
=

1
n-1

∑
i=1
n

(
xi
-
x¯
)
2

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

DOUBLE 类型标量/向量/表。

## 例子

```dolphindb
var(1 1 1);
// output
0
var(1 2 3);
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
var(m);
// output
[10,22.5]
```

相关函数： [covar](../c/covar.html) 和 [corr](../c/corr.html)
