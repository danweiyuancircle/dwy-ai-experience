---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mode.html
fetched_at: 2026-05-19T09:32:16Z
category: funcs
title: mode
sha1: dfeb3f8dab5bd5a3730070b86a5ac72df1a27166
---

# mode

## 语法

`mode(X)`

## 详情

若 *X* 为向量，计算 *X* 中出现次数最多的值。

若 *X* 为矩阵/表，计算其每列中出现次数最多的值，返回一个向量/表。

该函数通过 hash table 统计 *X* 中唯一值（key）出现的次数，当有多个次数最多的 key 时，返回
hash table 中的第一个 key。与所有其它聚合函数一致，该函数在计算时忽略 NULL 值。

注：

对于不同数据类型，该函数采用的 hash 算法不相同，因此输出结果可能不同。

DolphinDB `mode` 函数和 `scipy.stats.mode`
功能上相同，但存在以下差异：

- DolphinDB 支持单参数 `mode(x)`，用于直接计算向量/矩阵/表中数据的众数； SciPy 的
  `scipy.stats.mode` 支持多维数组，并可通过 `axis`
  参数指定计算维度。
- DolphinDB `mode` 仅返回 mode，不返回频率信息；SciPy `mode`
  返回结构化结果 `ModeResult(mode, count)`，同时返回众数及其出现次数。
- 当有多个众数时，DolphinDB 返回 hash table 中的第一个 key；而
  `scipy.stats.mode` 默认返回最小的众数。
- DolphinDB `mode` 中，空值不参与计算，而SciPy `mode`
  会忽略或单独处理 NaN（通过参数 *nan\_policy* 控制）。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

当 *X* 是标量或向量时，返回一个整型标量。

当 *X* 是矩阵时，返回一个整型向量。

当*X* 是表时，返回一个表。

## 例子

```dolphindb
mode 2;
// output: 2

mode 1 3 3 3 4 5 5;
// output: 3

mode `test;
// output: test

m=matrix(1 1 2 2 2 3, 4 4 5 6 6 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 1 | 4 |
| 2 | 5 |
| 2 | 6 |
| 2 | 6 |
| 3 | 6 |

```dolphindb
mode m;
// output: [2,6]
```

相关的中心趋势函数：[mean](mean.html) 和 [med](med.html)
