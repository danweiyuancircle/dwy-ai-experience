---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sqrt.html
fetched_at: 2026-05-19T09:39:55Z
category: funcs
title: sqrt
sha1: d1a3c9ebf4f27a3cefa323edaa789a60ed55106e
---

# sqrt

## 语法

`sqrt(X)`

## 详情

计算 *X* 中每个元素的平方根。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型的标量、向量或矩阵。

## 例子

```dolphindb
sqrt(4 16 -4 NULL);
// output
[2,4, , ]

typestr(sqrt(4));
// output
DOUBLE
```
