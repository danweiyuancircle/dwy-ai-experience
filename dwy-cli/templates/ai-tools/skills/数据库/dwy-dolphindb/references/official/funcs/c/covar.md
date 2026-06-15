---
source_url: https://docs.dolphindb.cn/zh/funcs/c/covar.html
fetched_at: 2026-05-19T09:16:04Z
category: funcs
title: covar
sha1: 823f460c63d69a01f3064f031adac1742708a8fd
---

# covar

## 语法

`covar(X,Y)`

别名：`cov`

## 详情

计算 *X* 和 *Y* 的协方差（covariance）。

## 参数

**Y** 和 **X** 是相同长度的数值型向量、维度相同的矩阵或表。若 *X* 是表，只对其内数值型和布尔型的列进行计算。

## 返回值

DOUBLE 类型标量/向量/表。

## 例子

```dolphindb
x=7 4 5 8 9 3 3 5 2 6 12 1 0 -5 32
y=1.1 7 8 9 9 5 4 8.6 2 1 -9 -3 5 8 13
covar(x,y);
// output
10.881429
```

相关函数：[covarp](covarp.html)
