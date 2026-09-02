---
source_url: https://docs.dolphindb.cn/zh/funcs/m/med.html
fetched_at: 2026-05-19T09:31:29Z
category: funcs
title: med
sha1: a6d008a7ad46b7aa4934f223b07f1e53d018d974
---

# med

## 语法

`med(X)`

## 详情

如果 *X* 是向量，返回 *X* 中所有元素的中值。

若 *X* 为矩阵，计算每列的中值，返回一个向量。

与所有其它聚合函数一致，计算时忽略 NULL 值。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
x=3 6 1 5 9;
med x;
// output: 5

m=matrix(1 2 10, 4 5 NULL);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 10 |  |

```dolphindb
med m;
// output: [2,4.5]
```

相关的中心趋势函数：[mean](mean.html) 和 [mode](mode.html)
