---
source_url: https://docs.dolphindb.cn/zh/funcs/i/intersection.html
fetched_at: 2026-05-19T09:27:54Z
category: funcs
title: intersection
sha1: f173f1f93376e7a91a1096d73b4ca28bb548e732
---

# intersection

## 语法

`intersection(X, Y)` 或 `X&Y`

## 详情

若 *X* 和 *Y* 均为集合，返回其交集。

若 *X* 和 *Y* 是相同长度的整形向量或标量，返回位运算 `AND`
的结果。

## 参数

**X** 和 **Y** 均为集合，或是相同长度的整型向量或标量。

## 返回值

集合、整型向量或标量。

## 例子

```dolphindb
x=set([5,5,3,4,6])
y=set(8 9 4 4 6)
x & y;

// output: set(4,6)

6 7 8 & 4 5 6;
// output
[4,5,0]
```
