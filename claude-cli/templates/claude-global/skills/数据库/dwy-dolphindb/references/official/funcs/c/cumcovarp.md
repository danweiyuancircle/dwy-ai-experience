---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumcovarp.html
fetched_at: 2026-05-19T09:17:26Z
category: funcs
title: cumcovarp
sha1: b04fbebbc16545833352eb5c5b822109e0a5eeca
---

# cumcovarp

首发版本：3.00.5

## 语法

`cumcovarp(X,Y)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum
系列）](../themes/cumFunctions.html)

## 详情

累积计算 *X* 和 *Y* 的总体协方差。

## 返回值

DOUBLE 类型，其数据形式取决于 *X* (*Y*)。

## 例子

```dolphindb
x = 7 4 5 8 9
y = 1 7 8 9 0
cumcovarp(x, y);
// output: [0,-4.5,-3.44,-0.75,-3.6]
```

相关函数：[covarp](covarp.html)
