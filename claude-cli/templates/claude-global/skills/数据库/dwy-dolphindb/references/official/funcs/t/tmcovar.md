---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmcovar.html
fetched_at: 2026-05-19T09:41:50Z
category: funcs
title: tmcovar
sha1: 40cfb6263700ea2169bda4b719f273055bc72cf2
---

# tmcovar

## 语法

`tmcovar(T, X, Y, window)`

参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间长度衡量）的滑动窗口内，计算 *X* 和 *Y* 元素的协方差。

## 返回值

DOUBLE 类型向量。

## 例子

```dolphindb
T = 1 1 1 2 5 6
X = 1 4 2 -1 2 4
Y = 2 5 -3 6 9 1
m = table(T as t,X as x, Y as y)
select *, tmcovar(t, y, x, 3) from m
```

| t | x | y | tmcovar\_t |
| --- | --- | --- | --- |
| 1 | 1 | 2 |  |
| 1 | 4 | 5 | 4.5 |
| 1 | 2 | -3 | 3.3333 |
| 2 | -1 | 6 | -1.6667 |
| 5 | 2 | 9 |  |
| 6 | 4 | 1 | -8 |

```dolphindb
T = 2021.01.02 2021.01.02  2021.01.04  2021.01.05 2021.01.07 2021.01.08
X = 1 4 2 -1 2 4
Y = 2 5 -3 6 9 1
m = table(T as t,X as x, Y as y)
select *, tmcovar(t, y, x, 3d) from m
```

| t | x | y | tmcovar\_t |
| --- | --- | --- | --- |
| 2021.01.02 | 1 | 2 |  |
| 2021.01.02 | 4 | 5 | 4.5 |
| 2021.01.04 | 2 | -3 | 3.3333 |
| 2021.01.05 | -1 | 6 | -13.5 |
| 2021.01.07 | 2 | 9 | 4.5 |
| 2021.01.08 | 4 | 1 | -8 |

```dolphindb
select *, tmcovar(t, y, x, 1w) from m
```

| t | x | y | tmcovar\_t |
| --- | --- | --- | --- |
| 2021.01.02 | 1 | 2 |  |
| 2021.01.02 | 4 | 5 | 4.5 |
| 2021.01.04 | 2 | -3 | 3.3333 |
| 2021.01.05 | -1 | 6 | -1.6667 |
| 2021.01.07 | 2 | 9 | -0.6 |
| 2021.01.08 | 4 | 1 | -1.6 |

相关函数：[mcovar](../m/mcovar.html), [covar](../c/covar.html)
