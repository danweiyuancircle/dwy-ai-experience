---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tmfirst.html
fetched_at: 2026-05-19T09:41:55Z
category: funcs
title: tmfirst
sha1: ba2a6ce11837b2ce8b9498a69034eaac8c6bf0e7
---

# tmfirst

## 语法

`tmfirst(T, X, window)`

参数说明和窗口计算规则请参考：[tmFunctions](../themes/tmFunctions.html)

## 详情

在给定长度（以时间 *T* 衡量）的滑动窗口内计算 *X* 的第一个元素。

## 返回值

返回一个与输入 *X* 相同数据类型的向量。

## 例子

```dolphindb
T = 1 1 1 2 5 6
X = 1 4 NULL -1 NULL 4
m = table(T as t,X as x)
select *, tmfirst(t, x, 3) from m
```

| t | x | tmfirst\_t |
| --- | --- | --- |
| 1 | 1 | 1 |
| 1 | 4 | 1 |
| 1 |  | 1 |
| 2 | -1 | 1 |
| 5 |  |  |
| 6 | 4 |  |

```dolphindb
T = 2021.01.02 2021.01.02  2021.01.04  2021.01.05 2021.01.07 2021.01.08
X = 3 4 NULL -1 2 4
m = table(T as t,X as x)
select *, tmfirst(t, x, 3d) from m
```

| t | x | tmfirst\_t |
| --- | --- | --- |
| 2021.01.02 | 3 | 3 |
| 2021.01.02 | 4 | 3 |
| 2021.01.04 |  | 3 |
| 2021.01.05 | -1 |  |
| 2021.01.07 | 2 | -1 |
| 2021.01.08 | 4 | 2 |

```dolphindb
select *, tmfirst(t, x, 1w) from m
```

| t | x | tmfirst\_t |
| --- | --- | --- |
| 2021.01.02 | 3 | 3 |
| 2021.01.02 | 4 | 3 |
| 2021.01.04 |  | 3 |
| 2021.01.05 | -1 | 3 |
| 2021.01.07 | 2 | 3 |
| 2021.01.08 | 4 | 3 |

相关函数：[mfirst](../m/mfirst.html), [first](../f/first.html)
