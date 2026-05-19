---
source_url: https://docs.dolphindb.cn/zh/funcs/themes/rowFunctions.html
fetched_at: 2026-05-19T09:44:34Z
category: funcs
title: 行计算系列（row 系列）
sha1: cb058a163f405574c34d3517d6817c607e4ad0ab
---

# 行计算系列（row 系列）

DolphinDB 中，绝大部分计算函数是基于向量、矩阵或表的一列进行的。若需要逐行计算，普通函数无法满足要求。为此，DolphinDB 设计了row
系列函数，可以满足用户逐行进行计算的需求。

## row 系列函数介绍

row 系列函数对应的高阶函数 [byRow](../ho_funcs/byRow.html)：

```dolphindb
byRow(func, X, [Y])
```

或

```dolphindb
byRow (:H)
```

内置的 row 系列函数的通用参数模板如下：

模板一：单目函数

```dolphindb
rowFunc(args…)
```

单目函数模板（2.00.10 版本首发）

```dolphindb
rowFunc(X)
```

模板二：双目函数(2.00.4版本首发)：

```dolphindb
rowFunc(X, Y)
```

## 参数（单目函数）

- **args**
  可以是单个标量/矩阵、一或多个向量/向量元组/表的组合。输入的各参数的行数（向量的长度/元组中每行向量的长度/表的行数）必须相同。

  注：

  矩阵逐行计算，返回一个长度和行数相同的向量，暂不支持输入多个矩阵进行计算。
- **X** 是矩阵/数组向量/列式元组/由等长向量组成的元组。其中，如下单目函数不支持输入 由等长向量组成的元组：rowRank, rowDenseRank,
  rowMove, rowNext, rowPrev。

## 参数（双目函数）

**X** 和 **Y** 是维度相同的矩阵/数值型向量/数组向量或由等长向量组成的元组。

如下二元函数支持同时接收列式元组作为入参：rowWavg, rowCorr,
rowCovar, rowCovarp, rowBeta, and rowWsum, rowCumwsum

## row系列函数一览

row 系列函数如下：

单目函数：

- [rowAnd](../r/rowAnd.html)
- [rowOr](../r/rowOr.html)
- [rowXor](../r/rowXor.html)
- [rowMax](../r/rowMax.html)
- [rowMin](../r/rowMin.html)
- [rowImax](../r/rowImax.html)
- [rowImin](../r/rowImin.html)
- [rowImaxLast](../r/rowimaxlast.html)
- [rowIminLast](../r/rowiminlast.html)
- [rowCount](../r/rowCount.html)
- [rowSize](../r/rowSize.html)
- [rowSum](../r/rowSum.html)
- [rowSum2](../r/rowSum2.html)
- [rowAvg](../r/rowAvg.html)
- [rowProd](../r/rowProd.html)
- [rowStd](../r/rowStd.html)
- [rowStdp](../r/rowStdp.html)
- [rowVar](../r/rowVar.html)
- [rowVarp](../r/rowVarp.html)
- [rowPrev](../r/rowPrev.html)
- [rowNext](../r/rowNext.html)
- [rowMove](../r/rowMove.html)
- [rowCumsum](../r/rowCumsum.html)
- [rowCumprod](../r/rowCumprod.html)
- [rowCummax](../r/rowCummax.html)
- [rowCummin](../r/rowCummin.html)

双目函数：

- [rowBeta](../r/rowBeta.html)
- [rowCorr](../r/rowCorr.html)
- [rowCovar](../r/rowCovar.html)
- [rowCovarp](../r/rowCovarp.html)
- [rowWavg](../r/rowWavg.html)
- [rowWsum](../r/rowWsum.html)
- [rowCumwsum](../r/rowCumwsum.html)
- [rowEuclidean](../r/rowEuclidean.html)
- [rowTanimoto](../r/rowTanimoto.html)
- [rowDot](../r/rowDot.html)

特殊单目函数：

- 只支持输入单个矩阵：

  - [rowRank](../r/rowRank.html)
  - [rowDenseRank](../r/rowDenseRank.html)
- 支持输入元组、矩阵和表：

  - [rowKurtosis](../r/rowKurtosis.html)
  - [rowSkew](../r/rowSkew.html)

特殊双目函数：

X 支持输入矩阵或数组向量，Y 支持输入向量或数组向量：

- [rowAt](../r/rowAt.html)
- [rowAlign](../r/rowAlign.html)

## 计算规则

![](../../images/rowfunc_1.png)

对于不同类型的组合计算的规则，可以参考上图，对应下例。

```dolphindb
vec = [1,2,3]
vec_tuple = [[3,4,5],[4,5,6]]
tb = table(7 8 9 as id, 8 9 10 as code)
print rowSum(vec, vec_tuple, tb)
// output: [23, 28, 33]
```

矩阵计算的用例如下：

```dolphindb
m = matrix(4 2 1 3 5 8, 1 2 5 9 0 1, 3 6 3 2 1 5)
print rowSum(m)
// output: [8, 10, 9, 14, 6, 14]
```
