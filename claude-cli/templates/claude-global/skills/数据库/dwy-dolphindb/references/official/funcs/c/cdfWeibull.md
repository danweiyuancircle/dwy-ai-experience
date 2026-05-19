---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfWeibull.html
fetched_at: 2026-05-19T09:14:49Z
category: funcs
title: cdfWeibull
sha1: 4ee43b7010f545d77f3602a8d27fb20eebc952d4
---

# cdfWeibull

## 语法

`cdfWeibull(alpha, beta, X)`

## 详情

返回 Weibull 分布的累计密度函数的值。

## 参数

形状参数 **alpha** 和 **beta** 都是正数。

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfWeibull(2.31, 0.627, [0.001, 0.5, 0.999]);
// output
[0, 0.447241, 0.946762]

cdfWeibull(2.31,0.627, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[0.014295, 0.166535, 0.447241, 0.724646, 0.90021]
```
