---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfF.html
fetched_at: 2026-05-19T09:14:40Z
category: funcs
title: cdfF
sha1: 4b23e0df55beb730b112318fcde1f525643bd42e
---

# cdfF

## 语法

`cdfF(numeratorDF, denominatorDF, X)`

## 详情

返回 F 分布的累计密度函数的值。

## 参数

**numeratorDF** 和 **denominatorDF** 都是正数，表示 F 分布的自由度。

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfF(2.31, 0.627, [0.001, 0.5, 0.999]);
// output
[0.000444, 0.245679, 0.35098]

cdfF(2.31,0.627, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[0.07078, 0.176153, 0.245679, 0.295996, 0.334766]
```
