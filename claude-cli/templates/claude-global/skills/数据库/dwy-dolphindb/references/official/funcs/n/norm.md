---
source_url: https://docs.dolphindb.cn/zh/funcs/n/norm.html
fetched_at: 2026-05-19T09:33:15Z
category: funcs
title: norm
sha1: 4cf7bf68d742268a3429f926e53e3f8681394414
---

# norm

## 语法

`norm(mean, std, count)`

## 详情

返回一个长度（维度）为 *count* 的向量（矩阵），服从期望值为 *mean*，标准差为 *std* 的正态分布。

与 Python 中 norm 的区别：numpy.linalg.norm 用于计算矩阵或向量的范数，scipy.stats.norm 可用于生成正态分布对象。

## 参数

**mean** 数值型标量，表示正态分布的期望值。

**std** 数值型标量，表示正态分布的标准差。

**count** 整型标量或数据对。若为标量，表示输出向量的长度；若为数据对，表示输出矩阵的维度。

## 返回值

DOUBLE 类型向量或矩阵。

## 例子

```dolphindb
norm(2.0,0.1,3);
// output
[2.026602,1.988621,2.101107]

mean norm(3,1,10000);
// output
3.007866

std norm(3,1,10000);
// output
0.995806

// 生成随机矩阵
norm(0, 1, 3:2)
```

| col1 | col2 |
| --- | --- |
| -0.5399 | -0.8475 |
| -1.0029 | 1.811 |
| -0.0485 | -0.4339 |
