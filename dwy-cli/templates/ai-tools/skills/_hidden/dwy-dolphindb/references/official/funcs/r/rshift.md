---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rshift.html
fetched_at: 2026-05-19T09:37:42Z
category: funcs
title: rshift
sha1: fddf41226975258261229b9b31bfb6656a5d43b3
---

# rshift

## 语法

`rshift(X, a)` 或 `X>>a`

## 详情

`rshift` 将参数按位右移。

## 参数

**X** 可以是标量、数据对、向量或矩阵

**a** 是移动的位数。

## 返回值

数据形式和类型与 X 相同的对象。

## 例子

```dolphindb
rshift(2048, 2);
// output
512

 1..10 >> 1;
// output
[0,1,1,2,2,3,3,4,4,5]

1:10>>1;
// output
0 : 5
```

相关函数：[lshift](../l/lshift.html)
