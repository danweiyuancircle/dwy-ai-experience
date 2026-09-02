---
source_url: https://docs.dolphindb.cn/zh/funcs/p/polynomial.html
fetched_at: 2026-05-19T09:34:22Z
category: funcs
title: polynomial
sha1: 870c13048675ec0d89983c04d45f23e362ee455d
---

# polynomial

## 语法

`polynomial(X, coeffs)`

## 详情

对于每个 *X* 中的元素，用多项式系数计算一个值。

## 参数

**X** 可以是标量或向量。

**coeffs** 是表示多项式系数向量。

## 返回值

返回一个和 *X* 相同长度的向量。

## 例子

计算![](../../images/polynomial.png)，*X* 的取值是 1..10。

```dolphindb
polynomial(1..10, 1 2 3);
// output
[6,17,34,57,86,121,162,209,262,321]
```
