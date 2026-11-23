---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tan.html
fetched_at: 2026-05-19T09:41:23Z
category: funcs
title: tan
sha1: d86d0ec4ffe97c6866ac51b1a062f6503ebec2c2
---

# tan

## 语法

`tan(X)`

## 详情

返回 *X* 的正切。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型，数据形式同 *X*。

## 例子

```dolphindb
tan(0 1 2);
// output
[0,1.557408,-2.185040]
```

相关函数：[asin](../a/asin.html), [acos](../a/acos.html), [atan](../a/atan.html), [sin](../s/sin.html), [cos](../c/cos.html), [asinh](../a/asinh.html), [acosh](../a/acosh.html), [atanh](../a/atanh.html), [sinh](../s/sinh.html), [cosh](../c/cosh.html), [tanh](tanh.html)
