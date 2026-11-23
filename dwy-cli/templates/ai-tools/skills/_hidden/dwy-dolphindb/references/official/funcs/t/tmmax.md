---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmmax.html
fetched_at: 2026-05-19T09:42:00Z
category: funcs
title: tmmax
sha1: 245ef06fa3d4e29bebae8399a8853a2f282e2bcd
---

# tmmax

## 语法

`tmmax(T, X, window)`

参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间 *T* 衡量）的滑动窗口内计算 *X* 元素的最大值。

## 返回值

*X* 为整型，返回 LONG 类型向量，*X* 为浮点数，返回 DOUBLE 类型向量。

## 例子

```dolphindb
T = 1 1 1 2 5 6
X = 1 4 NULL -1 NULL 4
m = table(T as t,X as x)
select *, tmmax(t, x, 3) from m
```

| t | x | tmmax\_t |
| --- | --- | --- |
| 1 | 1 | 1 |
| 1 | 4 | 4 |
| 1 |  | 4 |
| 2 | -1 | 4 |
| 5 |  |  |
| 6 | 4 | 4 |

```dolphindb
T = 2021.01.02 2021.01.02  2021.01.04  2021.01.05 2021.01.07 2021.01.08
X = NULL 4 NULL -1 2 4
m = table(T as t,X as x)
select *, tmmax(t, x, 3d) from m
```

| t | x | tmmax\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 | 4 |
| 2021.01.04 |  | 4 |
| 2021.01.05 | -1 | -1 |
| 2021.01.07 | 2 | 2 |
| 2021.01.08 | 4 | 4 |

```dolphindb
select *, tmmax(t, x, 1w) from m
```

| t | x | tmmax\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 | 4 |
| 2021.01.04 |  | 4 |
| 2021.01.05 | -1 | 4 |
| 2021.01.07 | 2 | 4 |
| 2021.01.08 | 4 | 4 |

相关函数：[mmax](../m/mmax.html), [max](../m/max.html)
