---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfLogistic.html
fetched_at: 2026-05-19T09:14:43Z
category: funcs
title: cdfLogistic
sha1: 6db053ef0c8c2fdcacff2d5b43875fc8d9300a27
---

# cdfLogistic

## 语法

`cdfLogistic(mean, s, X)`

## 详情

返回 Logistic 分布的累计密度函数的值。

## 参数

**mean** 是 Logistic 分布的均值。

**s** 是 Logistic 分布的尺度参数。

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfLogistic( 2.31, 0.627, [0.5, 0.3, 0.5, 0.7, 0.1]);
```

输出返回：[0.052812, 0.03895, 0.052812, 0.071241, 0.028617]
