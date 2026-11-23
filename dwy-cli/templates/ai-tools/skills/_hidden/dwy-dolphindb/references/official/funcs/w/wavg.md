---
source_url: https://docs.dolphindb.cn/zh/funcs/w/wavg.html
fetched_at: 2026-05-19T09:43:49Z
category: funcs
title: wavg
sha1: 7f6f6ca2c712cac28ab5ae8b51ad5704885e24fb
---

# wavg

## 语法

`wavg(X, Y)`

## 详情

对 *X*，以 *Y* 为权重，计算其加权平均数。

请注意，权重向量会自动调整，使得 *X* 向量中非 NULL 之值对应的权重向量之和为1。

## 参数

**X** 与 **Y** 是向量、矩阵或表。*Y* 表示权重。

## 返回值

一个数值型标量。

## 例子

```dolphindb
wavg(2.2 1.1 3.3, 4 5 6);
// output
2.273333
//  (2.2*4+1.1*5+3.3*6)/(4+5+6)

wavg(1 NULL 1, 1 1 1);
// output
1
```

相关函数：[wsum](wsum.html)
