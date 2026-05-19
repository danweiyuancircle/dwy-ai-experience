---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tanh.html
fetched_at: 2026-05-19T09:41:24Z
category: funcs
title: tanh
sha1: 7181e7e74df112a859151a37166970cd57904ab2
---

# tanh

## 语法

`tanh(X)`

## 详情

返回 *X* 的双曲正切。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型，数据形式同 *X*。

## 例子

```dolphindb
tanh(0 1 2);
// output
[0,0.761594,0.964028]
```

相关函数：[asin](../a/asin.html), [acos](../a/acos.html), [atan](../a/atan.html), [sin](../s/sin.html), [cos](../c/cos.html), [tan](tan.html), [asinh](../a/asinh.html), [acosh](../a/acosh.html), [atanh](../a/atanh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html)
