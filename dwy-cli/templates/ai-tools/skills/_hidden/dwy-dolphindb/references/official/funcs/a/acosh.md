---
source_url: https://docs.dolphindb.cn/zh/funcs/a/acosh.html
fetched_at: 2026-05-19T09:12:27Z
category: funcs
title: acosh
sha1: 32736788bd7a97ebd16ecee3293374db781ba9b3
---

# acosh

## 语法

`acosh(X)`

## 详情

返回 *X* 的反双曲余弦。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

返回结果的数据形式与输入保持一致：若输入为标量，返回标量；若输入为向量、矩阵或表，返回相同维度的结果。

## 例子

```dolphindb
acosh(1 2 3);
// output: [0,1.316958,1.762747]
```

相关函数：[asin](asin.html), [acos](acos.html), [atan](atan.html), [sin](../s/sin.html), [cos](../c/cos.html), [tan](../t/tan.html), [asinh](asinh.html), [atanh](atanh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
