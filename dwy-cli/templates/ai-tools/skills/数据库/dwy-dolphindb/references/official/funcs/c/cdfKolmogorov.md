---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfKolmogorov.html
fetched_at: 2026-05-19T09:14:42Z
category: funcs
title: cdfKolmogorov
sha1: f619ebee6fce0b127ea3698343ff504ab66fa01b
---

# cdfKolmogorov

## 语法

`cdfKolmogorov(X)`

## 详情

返回 Kolmogorov 分布的累计密度函数的值。

## 参数

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfKolmogorov([0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[1, 0.999991, 0.963945, 0.711235, 0.392731]

cdfKolmogorov([1,2,3]);
// output
[0.27, 0.000671, 3.045996E-8]
```
