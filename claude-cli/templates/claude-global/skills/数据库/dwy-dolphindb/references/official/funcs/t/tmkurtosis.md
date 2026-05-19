---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmkurtosis.html
fetched_at: 2026-05-19T09:41:56Z
category: funcs
title: tmkurtosis
sha1: 190f6e1138ef8a6e047d1cf86abc8aeaeba75917
---

# tmkurtosis

## 语法

`tmkurtosis(T, X, window, [biased=true])`

部分通用参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间 *T* 衡量）的滑动窗口内计算 *X* 的峰度。

## 参数

**biased** 是一个布尔值，表示是否是有偏估计。默认值为 true，表示有偏估计。

## 返回值

DOUBLE 类型向量。

## 例子

```dolphindb
T = 1 1 1 2 5 6
X = 1 4 NULL -1 NULL 4
m = table(T as t, X as x)
select *, tmkurtosis(t, x, 3) from m
```

| t | x | tmkurtosis\_t |
| --- | --- | --- |
| 1 | 1 |  |
| 1 | 4 |  |
| 1 |  |  |
| 2 | -1 | 1.5 |
| 5 |  |  |
| 6 | 4 |  |

```dolphindb
T = take(datehour(2019.06.13 13:30:10),4) join (datehour(2019.06.13 13:30:10)+1..6)
X = 1 NULL 3 4 5 NULL 3 NULL 5 3
m = table(T as t,X as x)
select *, tmkurtosis(t, x, 3d) from m
```

| t | x | tmkurtosis\_t |
| --- | --- | --- |
| 2019.06.13T13 | 1 |  |
| 2019.06.13T13 |  |  |
| 2019.06.13T13 | 3 |  |
| 2019.06.13T13 | 4 | 1.5 |
| 2019.06.13T14 | 5 | 1.8457 |
| 2019.06.13T15 |  | 1.8457 |
| 2019.06.13T16 | 3 | 2.2169 |
| 2019.06.13T17 |  | 2.2169 |
| 2019.06.13T18 | 5 | 2.2401 |
| 2019.06.13T19 | 3 | 2.4072 |

```dolphindb
select *, tmkurtosis(t, x, 1w) from m
```

| t | x | tmkurtosis\_t |
| --- | --- | --- |
| 2019.06.13T13 | 1 |  |
| 2019.06.13T13 |  |  |
| 2019.06.13T13 | 3 |  |
| 2019.06.13T13 | 4 | 1.5 |
| 2019.06.13T14 | 5 | 1.8457 |
| 2019.06.13T15 |  | 1.8457 |
| 2019.06.13T16 | 3 | 2.2169 |
| 2019.06.13T17 |  | 2.2169 |
| 2019.06.13T18 | 5 | 2.2401 |
| 2019.06.13T19 | 3 | 2.4072 |

相关函数：[mkurtosis](../m/mkurtosis.html), [kurtosis](../k/kurtosis.html)
