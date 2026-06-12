---
source_url: https://docs.dolphindb.cn/zh/funcs/a/asinh.html
fetched_at: 2026-05-19T09:13:17Z
category: funcs
title: asinh
sha1: 2d24fe6cc7d9988c85a71586c0a38557d75b6b18
---

# asinh

## 语法

`asinh(X)`

## 详情

计算 *X* 的反双曲正弦。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

返回结果的数据形式与输入保持一致：若输入为标量，返回标量；若输入为向量、矩阵或表，返回相同维度的结果。

## 例子

```dolphindb
asinh(0.841471 0.909297 0.141120);
// output
[0.764725,0.815761,0.140656]
```

相关函数：[asin](asin.html), [acos](acos.html), [atan](atan.html), [sin](../s/sin.html), [cos](../c/cos.html), [tan](../t/tan.html), [acosh](acosh.html), [atanh](atanh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html), [tanh](../t/tanh.html)
