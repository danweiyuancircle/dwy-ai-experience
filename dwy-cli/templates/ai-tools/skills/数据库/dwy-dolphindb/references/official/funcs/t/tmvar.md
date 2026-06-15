---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmvar.html
fetched_at: 2026-05-19T09:42:22Z
category: funcs
title: tmvar
sha1: ae220d2125db7e2410fedb1032b425adc1ca1668
---

# tmvar

## 语法

`tmvar(T, X, window)`

参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间 *T* 衡量）的滑动窗口内计算 *X* 的样本方差。

## 返回值

DOUBLE 类型向量。

## 例子

```dolphindb
T = 1 1 3 5 8 15 15 20
X = 5 2 4 1 2 8 9 10
m=table(T as t, X as x)
select *, tmvar(t, x, 3) from m
```

| t | x | tmvar\_t |
| --- | --- | --- |
| 1 | 5 |  |
| 1 | 2 | 4.5 |
| 3 | 4 | 2.3333 |
| 5 | 1 | 4.5 |
| 8 | 2 |  |
| 15 | 8 |  |
| 15 | 9 | 0.5 |
| 20 | 10 |  |

```dolphindb
T = 2021.01.02 2021.01.02  2021.01.04  2021.01.05 2021.01.07 2021.01.08
X = NULL 4 NULL -1 2 4
m = table(T as t,X as x)
select *, tmvar(t, x, 3d) from m
```

| t | x | tmvar\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 |  |
| 2021.01.04 |  |  |
| 2021.01.05 | -1 |  |
| 2021.01.07 | 2 | 4.5 |
| 2021.01.08 | 4 | 2 |

```dolphindb
select *, tmvar(t, x, 1w) from m
```

| t | x | tmvar\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 |  |
| 2021.01.04 |  |  |
| 2021.01.05 | -1 | 12.5 |
| 2021.01.07 | 2 | 6.333 |
| 2021.01.08 | 4 | 5.5833 |

相关函数：[mvar](../m/mvar.html), [var](../v/var.html)
