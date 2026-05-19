---
source_url: https://docs.dolphindb.cn/zh/funcs/themes/cumFunctions.html
fetched_at: 2026-05-19T09:44:30Z
category: funcs
title: 累计窗口系列（cum 系列）
sha1: 2971beedc912c9f0abe3ed7642b634bb60cb71c1
---

# 累计窗口系列（cum 系列）

累积窗口，即窗口的起始边界固定，结束边界逐步向右移动的窗口。针对累计窗口计算场景，DolphinDB 提供了 cum 系列函数。

## cum 系列函数介绍

cum 系列函数对应的高阶函数 [accumulate](../ho_funcs/accumulate.html)：

```dolphindb
accumulate(func, X, [init])
```

注：

如果指定了 *init*，第一个窗口的结果为 *init* + *X* [0]。

内置的 cum 系列函数的通用参数模板如下：

```dolphindb
cumfunc(X)
cumfunc(X, Y)
```

## 参数

**X** (**Y**) 是一个标量、向量、矩阵、表、元组（元素为标量或等长向量）、或字典。cum 系列函数如下：

单目：

- [cummax](../c/cummax.html)
- [cummin](../c/cummin.html)
- [cummed](../c/cummed.html)
- [cumfirstNot](../c/cumfirstNot.html)
- [cumlastNot](../c/cumlastNot.html)
- [cumrank](../c/cumrank.html)
- [cumcount](../c/cumcount.html)
- [cumpercentile](../c/cumpercentile.html)
- [cumstd](../c/cumstd.html)
- [cumstdp](../c/cumstdp.html)
- [cumvar](../c/cumvar.html)
- [cumvarp](../c/cumvarp.html)
- [cumsum](../c/cumsum.html)
- [cumsum2](../c/cumsum2.html)
- [cumsum3](../c/cumsum3.html)
- [cumsum4](../c/cumsum4.html)
- [cumavg](../c/cumavg.html)
- [cumprod](../c/cumprod.html)
- [cumnunique](../c/cumnunique.html)
- [cumPositiveStreak](../c/cumPositiveStreak.html)

双目：

- [cumbeta](../c/cumbeta.html)
- [cumwsum](../c/cumwsum.html)
- [cumwavg](../c/cumwavg.html)
- [cumcovar](../c/cumcovar.html)
- [cumcovarp](../c/cumcovarp.html)
- [cumcorr](../c/cumcorr.html)

## 窗口确定规则

cum
系列函数可以视为一个累计的窗口计算，对数据中的每一个元素，都会进行一次累计计算，因此返回一个和元数据等长的向量（相同维度的矩阵）。

其计算规则如下图：

![](../../images/cum_1.png)

上图的对应代码，这里以 [cumsum](../c/cumsum.html) 为例：

```dolphindb
X = 1 1 2 3 4 5 NULL 8 9 1 3
cumsum(X)

//output: [1, 2, 4, 7, 11, 16, 16, 24, 33, 34, 37]
```
