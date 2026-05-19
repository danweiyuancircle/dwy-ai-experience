---
source_url: https://docs.dolphindb.cn/zh/funcs/s/stdp.html
fetched_at: 2026-05-19T09:40:07Z
category: funcs
title: stdp
sha1: e5be84db11cc697a4bf2444a9af1a9e6b24974d2
---

# stdp

## 语法

`stdp(X)`

## 详情

若 *X* 为向量，返回 *X* 的总体标准差。

若 *X* 为矩阵，计算每列的总体标准差，返回一个向量。

若 *X* 为表，计算每列的总体标准差，返回一个表。

与所有其它聚合函数一致，计算时忽略 NULL 值。

## 参数

**X** 可以是向量、矩阵或表。

## 返回值

一个标量、向量或表。

## 例子

```dolphindb
stdp(1 2 3);
// output
0.816497

m=matrix(1 3 5 7 9, 1 4 7 10 13);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 1 |
| 3 | 4 |
| 5 | 7 |
| 7 | 10 |
| 9 | 13 |

```dolphindb
stdp(m);
// output
[2.8284,4.2426]
```

相关函数：[std](std.html), [cumstdp](../c/cumstdp.html)
