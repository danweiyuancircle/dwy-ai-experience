---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cosh.html
fetched_at: 2026-05-19T09:15:59Z
category: funcs
title: cosh
sha1: 10e1dce43f69bf8668c85d7844dbd5b254453186
---

# cosh

## 语法

`cosh(X)`

## 详情

返回 *X* 的双曲余弦。

注：

与 [numpy.cosh](https://numpy.com.cn/doc/stable/reference/generated/numpy.cosh.html) 函数的功能相同，区别在于 DolphinDB 的
`cosh` 函数只接受一个参数 *X*，不支持 `numpy.cosh` 中的
*out*、*where* 等参数。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型标量、向量或矩阵。

## 例子

```dolphindb
cosh 0 1 2;
// output
[1,1.543081,3.762196]
```

相关函数：[asin](../a/asin.html), [acos](../a/acos.html), [atan](../a/atan.html), [sin](../s/sin.html), [cos](cos.html), [tan](../t/tan.html), [asinh](../a/asinh.html), [acosh](../a/acosh.html), [atanh](../a/atanh.html), [sinh](../s/sinh.html), [tanh](../t/tanh.html)
