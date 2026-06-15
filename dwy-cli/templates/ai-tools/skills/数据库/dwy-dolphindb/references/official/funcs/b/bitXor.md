---
source_url: https://docs.dolphindb.cn/zh/funcs/b/bitXor.html
fetched_at: 2026-05-19T09:13:51Z
category: funcs
title: bitXor
sha1: 1f01e1aec440c2249427319b7cfdfee6c055711b
---

# bitXor

## 语法

`bitXor(X, Y)` 或 `X ^ Y`

## 详情

返回位运算异或（`bitXOr`）的结果。

## 参数

**X** 和 **Y** 可以是数值型的标量，向量，矩阵，或数据表。

## 返回值

数值类型标量/向量/矩阵/表。

## 例子

```dolphindb
x=1 0 1;
y= 0 1 1;
x^y;
// output
[1,1,0]
```
