---
source_url: https://docs.dolphindb.cn/zh/funcs/a/atan.html
fetched_at: 2026-05-19T09:13:22Z
category: funcs
title: atan
sha1: 5426e2891272f5cec2c546d606a9ca0a67b26233
---

# atan

## 语法

`atan(X)`

## 详情

返回 *X* 的反正切。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

返回结果的数据形式与输入保持一致：若输入为标量，返回标量；若输入为向量、矩阵或表，返回相同维度的结果。

## 例子

```dolphindb
atan 0.000000 1.557408 -2.185040;
// output
[0,1,-1.141593]
```

相关函数：[asin](asin.html), [acos](acos.html), [sin](../s/sin.html), [cos](../c/cos.html), [tan](../t/tan.html), [asinh](asinh.html), [acosh](acosh.html), [atanh](atanh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
