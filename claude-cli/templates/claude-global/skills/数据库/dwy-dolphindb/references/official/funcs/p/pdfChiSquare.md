---
source_url: https://docs.dolphindb.cn/zh/funcs/p/pdfChiSquare.html
fetched_at: 2026-05-19T09:34:00Z
category: funcs
title: pdfChiSquare
sha1: 5ed3fa1ab43d8c12f3f18f327bd7acc48561c13b
---

# pdfChiSquare

## 语法

`pdfChiSquare(df, X)`

## 详情

计算指定卡方分布在 X 处的概率密度。

其功能和用法同 scipy.stats.chi2.pdf 。

## 参数

**df** 数值型标量，代表自由度参数。

**X** 数值型标量或向量，代表要计算概率密度的点。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
pdfChiSquare(df=3, X=[1,2,3])
// output: [0.241970724519143, 0.207553748710297, 0.154180329803769]
```
