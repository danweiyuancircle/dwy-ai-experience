---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfExp.html
fetched_at: 2026-05-19T09:14:39Z
category: funcs
title: cdfExp
sha1: 2905510de27ef0b6ef91164fd550ee8c326f42c8
---

# cdfExp

## 语法

`cdfExp(mean, X)`

## 详情

返回指数分布的累计密度函数的值。

## 参数

**mean** 是指数分布的均值。

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfExp(1, [-1, 0, 0.5, 1, 2]);
// output
[0, 0, 0.393469, 0.632121, 0.864665]

cdfExp(1, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[0.095163, 0.259182, 0.393469, 0.503415, 0.59343]
```
