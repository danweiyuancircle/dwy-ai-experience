---
source_url: https://docs.dolphindb.cn/zh/funcs/w/wsum2.html
fetched_at: 2026-05-19T09:44:17Z
category: funcs
title: wsum2
sha1: 01553cb3dcfab98ad02151c06b4285cb106409fb
---

# wsum2

## 语法

`wsum2(X, Y)`

## 详情

返回 *X* 和 *Y* 的加权平方和。即使 *X* 和 *Y* 都是整型，返回结果仍为
DOUBLE 类型。

## 参数

**X** 和 **Y** 可以是标量、向量、矩阵或表。

## 返回值

DOUBLE 类型的标量/向量/表。

## 例子

```dolphindb
wsum2(3 4 1, 1 2 3);
// output
44
// 9*1 + 16*2 + 1*3 = 44
```

相关函数：[wsum](wsum.html)
