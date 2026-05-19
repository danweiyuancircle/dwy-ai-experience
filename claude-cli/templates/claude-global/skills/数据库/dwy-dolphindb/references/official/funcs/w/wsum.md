---
source_url: https://docs.dolphindb.cn/zh/funcs/w/wsum.html
fetched_at: 2026-05-19T09:44:15Z
category: funcs
title: wsum
sha1: c031c147d7a5263166f913318bb12e426c3cb176
---

# wsum

## 语法

`wsum(X, Y)`

## 详情

返回 *X* 和 *Y* 的内积。即使 *X* 和 *Y* 都是整型，返回结果仍为
DOUBLE 类型。

## 参数

**X** 和 **Y** 可以是标量、向量、矩阵或表。

## 返回值

DOUBLE 类型的标量/向量/表。

## 例子

```dolphindb
wsum(7 8 9, 1 2 3);
// output
50
// 7*1 + 8*2 + 9*3 = 50
```

相关函数：[wavg](wavg.html)
