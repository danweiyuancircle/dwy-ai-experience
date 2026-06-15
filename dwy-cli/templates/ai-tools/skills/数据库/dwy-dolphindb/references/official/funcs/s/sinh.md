---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sinh.html
fetched_at: 2026-05-19T09:39:24Z
category: funcs
title: sinh
sha1: 184660118f9ff4fce776a75b50f51f732b123542
---

# sinh

## 语法

`sinh(X)`

## 详情

返回 *X* 的双曲正弦。

注：

DolphinDB 的 `sinh` 函数仅接收单一参数，支持标量、向量及矩阵的计算；而 NumPy 的
`sinh` 函数作为通用 ufunc，支持任意维度的 N 维数组，并可通过
`out`、`where` 等参数实现指定输出与条件计算。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型的标量、向量或矩阵。

## 例子

```dolphindb
sinh 1 2 3;
// output
[1.175201,3.62686,10.017875]
```

相关函数：[asin](../a/asin.html), [acos](../a/acos.html), [atan](../a/atan.html), [sin](sin.html), [cos](../c/cos.html), [tan](../t/tan.html), [asinh](../a/asinh.html), [acosh](../a/acosh.html), [atanh](../a/atanh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
