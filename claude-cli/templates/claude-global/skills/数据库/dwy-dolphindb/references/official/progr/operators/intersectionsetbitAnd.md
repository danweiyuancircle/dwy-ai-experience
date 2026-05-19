---
source_url: https://docs.dolphindb.cn/zh/progr/operators/intersectionsetbitAnd.html
fetched_at: 2026-05-19T09:01:14Z
category: progr
title: intersection(set)/bitAnd(&)
sha1: 6cbca7b721ee45cc6b6882d399e543f4f735bf79
---

# intersection(set)/bitAnd(&)

## 语法

`X & Y`

## 参数

- 集合运算： **X** 和 **Y** 是集合。
- 位运算： **X** 和 **Y** 是长度相同的向量，或 **Y** 是标量。

## 详情

- 集合运算：返回两个集合的交集。
- 位运算：返回按位与运算的结果。

## 例子

```dolphindb
// 交集
x=set([5,5,3,4]);
y=set(8 9 4 4 6);
x & y;
// output
set(4)

// 按位与运算
x=1 0 1;
y=0 1 1;
x&y;
// output
[0,0,1]
```
