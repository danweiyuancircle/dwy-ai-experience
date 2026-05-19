---
source_url: https://docs.dolphindb.cn/zh/progr/operators/unionsetbitOr.html
fetched_at: 2026-05-19T09:01:34Z
category: progr
title: union(set)/bitOr(|)
sha1: 9d2f077ccebf9dfda41a94d5bdb8fd880b828a01
---

# union(set)/bitOr(|)

## 语法

- 集合运算： `X | Y` 或 `X union Y` 或
  `union(X,Y)`
- 位运算： `X | Y` 或 `X bitOr Y` 或 `bitOr(X,
  Y)`

## 参数

- 集合运算： **X** 和 **Y** 是集合。
- 位运算： **X** 和 **Y** 是长度相同的向量，或 **Y** 是标量。

## 详情

- 集合运算：返回两个集合的并集。
- 位运算：返回按位或运算的结果。

## 例子

```dolphindb
// 并集
x=set([5,5,3,4]);
y=set(8 9 9 4 6);
x | y;
// output
set(8,9,6,4,3,5)

// 按位或运算
x=1 0 1;
y=0 1 1;
x|y;
// output
[1,1,1]
```
