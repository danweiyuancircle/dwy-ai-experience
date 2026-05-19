---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cdfStudent.html
fetched_at: 2026-05-19T09:14:47Z
category: funcs
title: cdfStudent
sha1: f25f303d01b87703417d5ffe9e4efbe4af8e88f2
---

# cdfStudent

## 语法

`cdfStudent(df, X)`

## 详情

返回 t 分布的累计密度函数的值。

## 参数

**df** 是正数，表示 t 分布的自由度。

**X** 是数值型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
cdfStudent(1, [-1, 0, 0.5, 1, 2]);
// output
[0.25, 0.5, 0.647584, 0.75, 0.852416]

cdfStudent(1, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[0.531726, 0.592774, 0.647584, 0.6944, 0.733262]
```
