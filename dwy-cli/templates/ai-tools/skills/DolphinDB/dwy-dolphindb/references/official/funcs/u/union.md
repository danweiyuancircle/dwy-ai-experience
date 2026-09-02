---
source_url: https://docs.dolphindb.cn/zh/funcs/u/union.html
fetched_at: 2026-05-19T09:43:07Z
category: funcs
title: union
sha1: 2d23d44273f7b96bd799504a58d2d674087308dc
---

# union

## 语法

`union(X, Y)` 或 `X|Y`

## 详情

返回两个集合的并集。

## 参数

**X** 和 **Y** 是集合

## 返回值

一个集合。

## 例子

```dolphindb
x=set([5,5,3,4]);
y=set(8 9 9 4 6);
x | y;
// output: set(8,9,6,4,3,5)
```
