---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumbeta.html
fetched_at: 2026-05-19T09:17:19Z
category: funcs
title: cumbeta
sha1: 26c34f8ff44e1303508ca1b9a390fa5a1274fdf7
---

# cumbeta

## 语法

`cumbeta(Y, X)`

参数说明和窗口计算规则请参考: [累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

累积计算 *Y* 在 *X* 上的回归系数的最小二乘估计。

## 返回值

DOUBLE 类型，其数据形式取决于 *X* (*Y*)。

## 例子

```dolphindb
x=1 3 5 7 11 16 23
y=1 6 9 8 15 23 34;

cumbeta(y,x);
// output
[,2.5,2,1.2,1.256757,1.365322,1.440948]
```

相关函数：[beta](../b/beta.html)
