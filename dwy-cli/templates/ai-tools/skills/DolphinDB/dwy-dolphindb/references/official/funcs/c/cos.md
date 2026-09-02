---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cos.html
fetched_at: 2026-05-19T09:15:58Z
category: funcs
title: cos
sha1: 509a451e32f50c4f7218a6f9077f2eb63d4a8e83
---

# cos

## 语法

`cos(X)`

## 详情

返回 *X* 的余弦。

注：

与 [numpy.cos](https://numpy.com.cn/doc/stable/reference/generated/numpy.cos.html) 函数的功能相同，区别在于 DolphinDB 的
`cos` 函数只接受一个参数 *X*，不支持 `numpy.cos` 中的
*out*、*where* 等参数。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型标量、向量或矩阵。

## 例子

```dolphindb
cos 0 1 2;
// output
[1,0.540302,-0.416147]
```

相关函数：[asin](../a/asin.html), [acos](../a/acos.html), [atan](../a/atan.html), [sin](../s/sin.html), [tan](../t/tan.html), [asinh](../a/asinh.html), [acosh](../a/acosh.html), [atanh](../a/atanh.html), [sinh](../s/sinh.html), [cosh](cosh.html), [tanh](../t/tanh.html)
