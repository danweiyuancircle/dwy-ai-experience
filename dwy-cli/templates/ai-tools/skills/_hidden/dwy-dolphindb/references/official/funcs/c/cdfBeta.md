---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfBeta.html
fetched_at: 2026-05-19T09:14:35Z
category: funcs
title: cdfBeta
sha1: 61b44cbddcae991b3f3904065c004255b072bf1f
---

# cdfBeta

## 语法

`cdfBeta(alpha, beta, X)`

## 详情

返回 Beta 分布的累计密度函数的值。

## 参数

形状参数 **alpha** 和 **beta** 都是正数。

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfBeta(2.31, 0.627, [0.001, 0.5, 0.999]);
// output
[0, 0.116056, 0.976416]

cdfBeta(2.31, 0.627, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[0.002451, 0.032995, 0.116056, 0.280532, 0.597694]
```
