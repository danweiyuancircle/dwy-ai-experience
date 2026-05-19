---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmprod.html
fetched_at: 2026-05-19T09:42:08Z
category: funcs
title: tmprod
sha1: e4dd08f7dcd44a271531ccfd08f99ae55aaf9ae1
---

# tmprod

## 语法

`tmprod(T, X, window)`

参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间 *T* 衡量）的滑动窗口内计算 *X* 元素的乘积。

## 返回值

与 *X* 长度相同的 DOUBLE 类型向量。

## 例子

```dolphindb
T = 1 1 3 5 8 15 15 20
X = 5 2 4 1 2 8 9 10
m=table(T as t, X as x)
select *, tmprod(t, x, 3) from m
```

| t | x | tmprod\_t |
| --- | --- | --- |
| 1 | 5 | 5 |
| 1 | 2 | 10 |
| 3 | 4 | 40 |
| 5 | 1 | 4 |
| 8 | 2 | 2 |
| 15 | 8 | 8 |
| 15 | 9 | 72 |
| 20 | 10 | 10 |

```dolphindb
T = 2021.01.02 2021.01.02  2021.01.04  2021.01.05 2021.01.07 2021.01.08
X = NULL 4 NULL -1 2 4
m = table(T as t,X as x)
select *, tmprod(t, x, 3d) from m
```

| t | x | tmprod\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 | 4 |
| 2021.01.04 |  | 4 |
| 2021.01.05 | -1 | -1 |
| 2021.01.07 | 2 | -2 |
| 2021.01.08 | 4 | 8 |

```dolphindb
select *, tmprod(t, x, 1w) from m
```

| t | x | tmprod\_t |
| --- | --- | --- |
| 2021.01.02 |  |  |
| 2021.01.02 | 4 | 4 |
| 2021.01.04 |  | 4 |
| 2021.01.05 | -1 | -1 |
| 2021.01.07 | 2 | -2 |
| 2021.01.08 | 4 | 8 |

相关函数：[mprod](../m/mprod.html), [prod](../p/prod.html)
