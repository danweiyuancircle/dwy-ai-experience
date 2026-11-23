---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmmin.html
fetched_at: 2026-05-19T09:42:03Z
category: funcs
title: tmmin
sha1: 5138de38e6498f2db449dc49b24e1d2ad543d1e6
---

# tmmin

## 语法

`tmmin(T, X, window)`

参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间 *T* 衡量）的滑动窗口内计算 *X* 元素的最小值。

## 返回值

*X* 为整型，返回 LONG 类型向量，*X* 为浮点数，返回 DOUBLE 类型向量。

## 例子

```dolphindb
T = 1 1 1 2 5 6
X = 1 4 NULL -1 NULL 4
m = table(T as t,X as x)
select *, tmmin(t, x, 3) from m
```

| t | x | tmmin\_t |
| --- | --- | --- |
| 1 | 1 | 1 |
| 1 | 4 | 1 |
| 1 |  | 1 |
| 2 | -1 | -1 |
| 5 |  |  |
| 6 | 4 | 4 |

```dolphindb
T = 2021.01.02 2021.01.02  2021.01.04  2021.01.05 2021.01.07 2021.01.08
X = NULL 4 NULL -1 2 4
m = table(T as t,X as x)
select *, tmmin(t, x, 3d) from m
```

| t | x | tmmin\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 | 4 |
| 2021.01.04 |  | 4 |
| 2021.01.05 | -1 | -1 |
| 2021.01.07 | 2 | -1 |
| 2021.01.08 | 4 | 2 |

```dolphindb
select *, tmmin(t, x, 1w) from m
```

| t | x | tmmin\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 | 4 |
| 2021.01.04 |  | 4 |
| 2021.01.05 | -1 | -1 |
| 2021.01.07 | 2 | -1 |
| 2021.01.08 | 4 | -1 |

相关函数：[mmin](../m/mmin.html), [min](../m/min.html)
