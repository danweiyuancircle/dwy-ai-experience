---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmcorr.html
fetched_at: 2026-05-19T09:41:47Z
category: funcs
title: tmcorr
sha1: 0e1a19f2bf1a0a1c5f92eff03cb47f56b0ea1126
---

# tmcorr

## 语法

`tmcorr(T, X, Y, window)`

参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间长度衡量）的滑动窗口内，计算 *X* 和 *Y* 元素的相关性。

## 返回值

DOUBLE 类型向量。

## 例子

```dolphindb
T = 1 1 1 2 5 6
X = 1 4 2 -1 2 4
Y = 2 5 -3 6 9 1
m = table(T as t,X as x, Y as y)
select *, tmcorr(t, y, x, 3) from m
```

| t | x | y | tmcorr\_t |
| --- | --- | --- | --- |
| 1 | 1 | 2 |  |
| 1 | 4 | 5 | 1 |
| 1 | 2 | -3 | 0.5399 |
| 2 | -1 | 6 | -0.1981 |
| 5 | 2 | 9 |  |
| 6 | 4 | 1 | -1 |

```dolphindb
T = 2021.01.02 2021.01.02  2021.01.04  2021.01.05 2021.01.07 2021.01.08
X = 1 4 2 -1 2 4
Y = 2 5 -3 6 9 1
m = table(T as t,X as x, Y as y)
select *, tmcorr(t, y, x, 3d) from m
```

| t | x | y | tmcorr\_t |
| --- | --- | --- | --- |
| 2021.01.02 | 1 | 2 |  |
| 2021.01.02 | 4 | 5 | 1 |
| 2021.01.04 | 2 | -3 | 0.5399 |
| 2021.01.05 | -1 | 6 | -1 |
| 2021.01.07 | 2 | 9 | 1 |
| 2021.01.08 | 4 | 1 | -1 |

```dolphindb
select *, tmcorr(t, y, x, 1w) from m
```

| t | x | y | tmcorr\_t |
| --- | --- | --- | --- |
| 2021.01.02 | 1 | 2 |  |
| 2021.01.02 | 4 | 5 | 1 |
| 2021.01.04 | 2 | -3 | 0.5399 |
| 2021.01.05 | -1 | 6 | -0.1981 |
| 2021.01.07 | 2 | 9 | -0.0726 |
| 2021.01.08 | 4 | 1 | -0.1995 |

相关函数：[mcorr](../m/mcorr.html), [corr](../c/corr.html)
