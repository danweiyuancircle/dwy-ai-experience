---
source_url: https://docs.dolphindb.cn/zh/funcs/a/asin.html
fetched_at: 2026-05-19T09:13:16Z
category: funcs
title: asin
sha1: 8416adfb507bccb871449669d8089edadee8a56e
---

# asin

## 语法

`asin(X)`

## 详情

返回 *X* 的反正弦。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

返回结果的数据形式与输入保持一致：若输入为标量，返回标量；若输入为向量、矩阵或表，返回相同维度的结果。

## 例子

```dolphindb
asin(0 0.5 1);
// output
[0,0.523599,1.570796]
```

相关函数：[acos](acos.html), [atan](atan.html), [sin](../s/sin.html), [cos](../c/cos.html), [tan](../t/tan.html), [asinh](asinh.html), [acosh](acosh.html), [atanh](atanh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
