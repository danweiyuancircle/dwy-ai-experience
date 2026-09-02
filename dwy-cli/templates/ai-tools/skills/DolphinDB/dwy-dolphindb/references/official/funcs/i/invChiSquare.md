---
source_url: https://docs.dolphindb.cn/zh/funcs/i/invChiSquare.html
fetched_at: 2026-05-19T09:27:57Z
category: funcs
title: invChiSquare
sha1: a31463b48e0f159e85cc0b7ea3543fd8e42b8d32
---

# invChiSquare

## 语法

`invChiSquare(df, X)`

## 详情

返回卡方分布的累计密度函数的逆函数值。

## 参数

**df** 是正数，表示卡方分布的自由度。

**X** 是0到1之间的浮点型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
invChiSquare(1, [0, 0.05, 0.15, 0.25]);
// output
[0, 0.003932, 0.035766, 0.101531]

invChiSquare(1, [0.1, 0.3, 0.5, 0.7, 0.9]);

// output
[0.015791, 0.148472, 0.454936, 1.074194, 2.705543]
```
