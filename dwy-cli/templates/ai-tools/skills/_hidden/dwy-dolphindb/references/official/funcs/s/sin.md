---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sin.html
fetched_at: 2026-05-19T09:39:23Z
category: funcs
title: sin
sha1: 53b07485d484caecc5f6e3a9222982e770d0d53f
---

# sin

## 语法

`sin(X)`

## 详情

返回 *X* 的正弦。

注：

DolphinDB 的 `sin` 函数仅单一参数，支持标量、向量及矩阵计算；而 NumPy 的
`sin` 函数作为通用 ufunc，支持任意维度的 N 维数组，并可通过 *out*、*where*等参数实现指定输出与条件计算。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型的标量、向量或矩阵。

## 例子

```dolphindb
sin(1 2 3);
// output
[0.841471,0.909297,0.141120]
```

相关函数：[asin](../a/asin.html), [acos](../a/acos.html), [atan](../a/atan.html), [cos](../c/cos.html), [tan](../t/tan.html), [asinh](../a/asinh.html), [acosh](../a/acosh.html), [atanh](../a/atanh.html), [sinh](sinh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
