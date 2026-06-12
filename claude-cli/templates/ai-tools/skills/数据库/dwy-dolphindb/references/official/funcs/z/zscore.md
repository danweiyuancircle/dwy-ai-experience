---
source_url: https://docs.dolphindb.cn/zh/funcs/z/zscore.html
fetched_at: 2026-05-19T09:44:27Z
category: funcs
title: zscore
sha1: 96fb6bacaf2eed3b78ca0632e6fe422ec19c6830
---

# zscore

## 语法

`zscore(X)`

## 详情

若 *X* 为向量，为 *X* 中的每个元素计算标准分数（z-score）。

若 *X* 为矩阵或表，上述计算对每列分别进行。

计算中使用了样本标准差，而不是总体标准差。

## 参数

**X** 是一个向量、矩阵或表。

## 返回值

若 *X* 为向量，返回一个与 *X* 长度相等的向量；若 *X* 为矩阵或表，返回一个与
*X* 行列数相同的矩阵或表。

## 例子

```dolphindb
zscore(1 2 3 4 5);
// output
[-1.264911,-0.632456,0,0.632456,1.264911]

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
zscore(m);
```

| #0 | #1 |
| --- | --- |
| -1 | -1 |
| 0 | 0 |
| 1 | 1 |
