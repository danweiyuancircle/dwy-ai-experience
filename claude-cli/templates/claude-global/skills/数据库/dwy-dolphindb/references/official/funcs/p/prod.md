---
source_url: https://docs.dolphindb.cn/zh/funcs/p/prod.html
fetched_at: 2026-05-19T09:34:32Z
category: funcs
title: prod
sha1: 23ca799bfbba11d025413e2b32d12d172647e1aa
---

# prod

## 语法

`prod(X)`

## 详情

- 若 *X* 为向量，返回 *X* 中所有元素的乘积。
- 若 *X* 为矩阵，计算每列中所有元素的乘积，返回一个向量。
- 若 *X* 为表，计算每列中所有元素的乘积，返回一个表。

与所有其它聚合函数一致，计算时忽略 NULL 值。

DolphinDB 的 `prod` 函数对矩阵和表固定按列计算乘积；NumPy 默认将数组展平后计算全局乘积，需通过
*axis* 参数指定维度。此外，NumPy 支持指定 *axis* 参数按多轴计算，*initial* 设置初始值。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

数值型标量、向量、矩阵或表。

## 例子

```dolphindb
prod(1 2 NULL 3);
// output
6
```

```dolphindb
m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
prod(m);
// output
[6,120]
```
