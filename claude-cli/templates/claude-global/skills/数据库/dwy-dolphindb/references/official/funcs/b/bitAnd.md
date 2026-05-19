---
source_url: https://docs.dolphindb.cn/zh/funcs/b/bitAnd.html
fetched_at: 2026-05-19T09:13:48Z
category: funcs
title: bitAnd
sha1: c629c575f4044187fa8ae9381c12b8b35e85e2b9
---

# bitAnd

## 语法

`bitAnd(X, Y)` 或 `X & Y`

## 详情

返回位运算与（`bitAnd`）的结果。

## 参数

**X** 和 **Y** 可以是数值型的标量，向量，矩阵，或数据表。

## 返回值

数值类型标量/向量/矩阵/表。

## 例子

```dolphindb
x=1 0 1;
y=0 1 1;
x&y;
// output
[0,0,1]
```
