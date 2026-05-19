---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfGamma.html
fetched_at: 2026-05-19T09:14:41Z
category: funcs
title: cdfGamma
sha1: 77970ea12d5c1a5345d52b62902e0490771cc213
---

# cdfGamma

## 语法

`cdfGamma(shape, scale, X)`

## 详情

返回 Gamma 分布的累计密度函数的值。

## 参数

形状参数 **shape** 是正数。

尺度参数 **scale** 是正数。

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfGamma(2.31, 0.627, [0.001, 0.5, 0.999]);
// output
[0, 0.127367, 0.38032]

cdfGamma(2.31,0.627, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[0.004754, 0.048388, 0.127367, 0.225351, 0.329391]
```
