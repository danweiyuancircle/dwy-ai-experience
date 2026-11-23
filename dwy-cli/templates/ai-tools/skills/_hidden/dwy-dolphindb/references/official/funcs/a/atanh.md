---
source_url: https://docs.dolphindb.cn/zh/funcs/a/atanh.html
fetched_at: 2026-05-19T09:13:23Z
category: funcs
title: atanh
sha1: 018dc2939243bd96ff981450ba542d2bb509f020
---

# atanh

## 语法

`atanh(X)`

## 详情

返回 *X* 的反双曲正切。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

返回结果的数据形式与输入保持一致：若输入为标量，返回标量；若输入为向量、矩阵或表，返回相同维度的结果。

## 例子

```dolphindb
atanh 0.000000 0.557408 -0.185040;
// output
[0,0.629065,-0.187196]
```

相关函数：[asin](asin.html), [acos](acos.html), [atan](atan.html), [sin](../s/sin.html), [cos](../c/cos.html), [tan](../t/tan.html), [asinh](asinh.html), [acosh](acosh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
