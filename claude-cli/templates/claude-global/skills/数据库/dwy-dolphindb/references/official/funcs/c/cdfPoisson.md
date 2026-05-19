---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfPoisson.html
fetched_at: 2026-05-19T09:14:46Z
category: funcs
title: cdfPoisson
sha1: 13cd4aa2d2543bc730a8dae339c605a8f8e11382
---

# cdfPoisson

## 语法

`cdfPoisson(mean, X)`

## 详情

返回泊松分布的累计分布函数的值。

## 参数

**mean** 是泊松分布的均值。

**X** 是整型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfPoisson(1, [-1, 0, 1, 2, 3]);
// output
[0, 0.367879, 0.735759, 0.919699, 0.981012]

cdfPoisson(1, [1, 3, 5, 7, 9]);
// output
[0.735759, 0.981012, 0.999406, 0.99999, 1]
```
