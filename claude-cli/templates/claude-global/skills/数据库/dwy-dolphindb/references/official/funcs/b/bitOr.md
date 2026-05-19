---
source_url: https://docs.dolphindb.cn/zh/funcs/b/bitOr.html
fetched_at: 2026-05-19T09:13:50Z
category: funcs
title: bitOr
sha1: 06a04bac941772751be7a23e97a35a72a501846b
---

# bitOr

## 语法

`bitOr(X, Y)` 或 `X | Y`

## 详情

返回位运算或（`bitOr`）的结果。

## 参数

**X** 和 **Y** 可以是数值型的标量，向量，矩阵，或数据表。

## 返回值

数值类型标量/向量/矩阵/表。

## 例子

```dolphindb
x=1 0 1;
y=0 1 1;
x | y;
// output
[1,1,1]
```
