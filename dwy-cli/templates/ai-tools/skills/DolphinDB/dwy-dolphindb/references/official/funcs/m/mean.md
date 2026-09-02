---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mean.html
fetched_at: 2026-05-19T09:31:28Z
category: funcs
title: mean
sha1: c2f899369566cab7eabd376bec617a9194f48b3a
---

# mean

## 语法

`mean(X)`

## 详情

若 *X* 为向量，计算 *X* 的平均值。

若 *X* 为矩阵，计算每列的平均值。

若 *X* 为表，计算每列的平均值。

该函数与 [avg](../a/avg.html) 函数完全相同。

与所有其它聚合函数一致，计算时忽略 NULL 值。

DolphinDB `mean`
函数面向向量、矩阵和表。对于矩阵和表，默认按列计算均值，不存在“全局均值”概念，若需全局均值必须手动展平数据。NumPy 的 `mean`
函数面向多维数组。默认将输入展平为1维数组后计算全局均值；需显式指定 *axis* 参数才能按行、列或多轴计算。

## 参数

**X** 可以是标量、数据对、向量、矩阵或表。

## 返回值

若 *X* 为向量，返回一个 DOUBLE 标量。

若 *X* 为矩阵，返回一个 DOUBLE 向量。

若 *X* 为表，返回一个表。

## 例子

```dolphindb
x=1 5 9;
mean(x);
// output: 5

x=1 5 9 NULL;
mean(x);
// output
5

avg(x);
// output
5

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
mean(m);
// output
[2,5]
```

相关的中心趋势函数：[mode](mode.html), [med](med.html)
