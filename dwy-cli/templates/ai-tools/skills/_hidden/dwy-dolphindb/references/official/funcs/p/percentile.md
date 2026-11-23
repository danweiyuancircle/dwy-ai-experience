---
source_url: https://docs.dolphindb.cn/zh/funcs/p/percentile.html
fetched_at: 2026-05-19T09:34:06Z
category: funcs
title: percentile
sha1: 858cb320d84fd5430b803b96c93d1ca7c0f080c5
---

# percentile

## 语法

`percentile(X, percent, [interpolation='linear'])`

## 详情

若 *X* 是一个向量，计算其指定的百分位数。与所有其它聚合函数一致，计算时忽略 NULL 值。

若 *X* 为矩阵，计算每列的指定的百分位数，返回一个向量。

若 *X* 为表，计算每列的指定的百分位数，返回一个表。

与 Python 中 percentile 的区别：当 *X* 为矩阵时，numpy.percentile
默认会把整个矩阵展平成一维后算一个值，DolphinDB 的 percentile 会对每列分别计算，其行为相当于
`numpy.percentile(X, percent, axis=0)`。

## 参数

**X** 是一个向量、矩阵或表。

**percent** 是 0 到 100 之间的整数或小数。

**interpolation** 是一个字符串，表示当选中的分位点位于在 *X* 的第 i 和第 i+1
个元素之间时，采用的插值方法。它具有以下取值：

- 'linear': ![](../../images/linear.png), 其中 ![](../../images/fraction.png)
- 'lower': ![](../../images/xi.png)
- 'higher': ![higher](../../images/higher.png)
- 'nearest': ![](../../images/xi.png)和 ![](../../images/higher.png)之中最接近分位点的数据
- 'midpoint': ![](../../images/midpoint.png)

如果没有指定 *interpolation*，默认采用 'linear'。

## 返回值

DOUBLE 类型标量/向量，或一个包含 DOUBLE 类型结果的表。

## 例子

```dolphindb
a=[6, 47, 49, 15, 42, 41, 7, 39, 43, 40, 36];

percentile(a,50);
// output
40

percentile(a,54);
// output
40.4

percentile(a,25,"lower");
// output
15

percentile(a,75,"higher");
// output
43

percentile(a,5,"midpoint");
// output
6.5

percentile(a,5,"nearest");
// output
6
```

```dolphindb
m=matrix(1 2 5 3 4, 5 4 1 2 3);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 5 |
| 2 | 4 |
| 5 | 1 |
| 3 | 2 |
| 4 | 3 |

```dolphindb
percentile(m, 75);
[4,4]
```

相关函数：[quantile](../q/quantile.html)
