---
source_url: https://docs.dolphindb.cn/zh/funcs/q/quantile.html
fetched_at: 2026-05-19T09:34:45Z
category: funcs
title: quantile
sha1: 486d8ebedbab7313a11df865378cbc4c581ebd3a
---

# quantile

## 语法

`quantile(X, q, [interpolation='linear'])`

## 详情

计算 *X* 的分位数。

DolphinDB 的 `quantile` 语法精简且原生忽略空值，适合海量数据实时计算；NumPy 的
`quantile` 专为多维数组设计，支持传入数组批量计算多个分位点；SciPy 的
`quantile` 不仅支持为每个数据切片指定不同分位数，还支持 Harrell-Davis 统计估计器及
*nan\_policy* 参数，可以原生处理含缺失值的样本。

## 参数

**X** 是一个数值型向量、矩阵或表。

**q** 是0到1之间的浮点数。

**interpolation** 是一个字符串，表示当选中的分位点位于 i 和 j 之间时，采用的插值方法。它具有以下取值：

- 'linear': i+(j-1)\*fraction, fraction 是 size(X)\*q
  的小数部分
- 'lower':i
- 'higher': j
- 'nearest': i 和 j 之中最接近分位点的数据
- 'midpoint': (i+j)/2

如果没有指定 *interpolation*，默认采用 'linear'。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
a=[6, 47, 49, 15, 42, 41, 7, 39, 43, 40, 36];
quantile(a,0.25);
// output
25.5

quantile(a,0.5);
// output
40

quantile(a,0.75);
// output
42.5

quantile(a,0.75, 'lower');
// output
42
```

相关函数：[quantileSeries](quantileSeries.html), [percentile](../p/percentile.html)
