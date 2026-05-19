---
source_url: https://docs.dolphindb.cn/zh/funcs/s/seuclidean.html
fetched_at: 2026-05-19T09:39:11Z
category: funcs
title: seuclidean
sha1: 7abd15c29cadc498f93d292b247ff3970a0c16b9
---

# seuclidean

首发版本：3.00.5，3.00.4.3

## 语法

```dolphindb
seuclidean(X, Y, Z)
```

## 详情

计算两个数值向量（X 和 Y）之间的标准化欧式距离，先将 X 和 Y 分别标准化处理后，再调用 [euclidean](../e/euclidean.html)。公式定义如下：

![](../../images/seuclidean.png)

## 参数

**X** 数值向量。

**Y** 数值向量。

**Z** 数值向量，表示各维度的方差，用于标准化。

注：

*X*
、*Y*、*Z* 三者的长度必须相等。

## 返回值

DOUBLE 类型标量。

## 例子

```dolphindb
X = [2, 5]
Y = [3, 7]
Z = [1, 2]

seuclidean(X, Y, Z)
// 输出：1.7320508075688772
```

**相关函数**

[euclidean](../e/euclidean.html)、[minkowski](../m/minkowski.html)、[mahalanobis](../m/mahalanobis.html)
