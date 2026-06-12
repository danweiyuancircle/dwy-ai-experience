---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lowerbound.html
fetched_at: 2026-05-19T09:30:31Z
category: funcs
title: lowerBound
sha1: c6c197409cbf74be02d0f7f63b8d141c7df81eea
---

# lowerBound

## 语法

`lowerBound(X,Y)`

## 详情

对于 *Y* 中的每个元素 y，该函数返回 *X* 中第一个不小于 y 的元素下标。如果没有找到，则返回 *X* 的长度。

## 参数

**X** 递增的向量、索引序列、索引矩阵

**Y** 标量、向量、数组向量、元组、矩阵、字典、表

## 返回值

返回数值类型的结果，形式与 *Y* 一致。

## 例子

在以下例子中，X 中的部分元素大于或等于 Y 中的部分元素：

```dolphindb
X = [1,3,5];
Y = [5,6,7];
Z = lowerBound(X,Y);
Z
// output: [2,3,3]

index = [2023.05.04, 2023.05.06, 2023.05.07, 2023.05.10]
s = indexedSeries(index, 1..4)
y=[2023.05.04, 2023.05.06, 2023.05.09]

lowerBound(s,y)
```

| label | #0 |
| --- | --- |
| 2023.05.04 | 1 |
| 2023.05.06 | 2 |
| 2023.05.09 | 4 |
