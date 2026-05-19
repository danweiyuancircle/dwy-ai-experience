---
source_url: https://docs.dolphindb.cn/zh/funcs/a/acos.html
fetched_at: 2026-05-19T09:12:26Z
category: funcs
title: acos
sha1: 9f181a278d3d756422990c9e68913181b436836f
---

# acos

## 语法

`acos(X)`

## 详情

返回 *X* 的反余弦。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

返回结果的数据形式与输入保持一致：若输入为标量，返回标量；若输入为向量、矩阵或表，返回相同维度的结果。

## 例子

```dolphindb
acos(1.000000 0.540302 -0.416147);
// output: [0,1,2]
```

相关函数：[asin](asin.html), [atan](atan.html), [sin](../s/sin.html), [cos](../c/cos.html), [tan](../t/tan.html), [asinh](asinh.html), [acosh](acosh.html), [atanh](atanh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
