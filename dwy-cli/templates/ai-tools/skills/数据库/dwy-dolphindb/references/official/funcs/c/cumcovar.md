---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumcovar.html
fetched_at: 2026-05-19T09:17:24Z
category: funcs
title: cumcovar
sha1: 3780b0be20e54c7ac36ef597e3fb2bebad5a640a
---

# cumcovar

## 语法

`cumcovar(X,Y)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

累积计算 *X* 和 *Y* 的协方（covariance）。

## 返回值

DOUBLE 类型，其数据形式取决于 *X* (*Y*)。

## 例子

```dolphindb
x = 7 4 5 8 9
y = 1 7 8 9 0
cumcovar(x, y);
// output
[,-9,-5.166667,-1,-4.5]
```

相关函数：[covar](covar.html)
