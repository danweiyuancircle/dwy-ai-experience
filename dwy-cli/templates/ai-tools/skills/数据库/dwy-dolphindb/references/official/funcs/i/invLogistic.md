---
source_url: https://docs.dolphindb.cn/zh/funcs/i/invLogistic.html
fetched_at: 2026-05-19T09:28:03Z
category: funcs
title: invLogistic
sha1: 28e8a41f8369f581c1c44d24736875c16a6225af
---

# invLogistic

## 语法

`invLogistic(mean, s, X)`

## 详情

返回 Logistic 分布的累计密度函数的逆函数值。

## 参数

**mean** 是 Logistic 分布的均值。

**s** 是Logistic分布的尺度参数。

**X** 是0到1之间的浮点型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
invLogistic( 2.31, 0.627, [0.5, 0.3, 0.5, 0.7, 0.1]);
// output: [2.31, 1.778744, 2.31, 2.841256, 0.93234]
```
