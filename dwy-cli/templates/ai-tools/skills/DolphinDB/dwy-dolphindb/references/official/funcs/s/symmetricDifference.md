---
source_url: https://docs.dolphindb.cn/zh/funcs/s/symmetricDifference.html
fetched_at: 2026-05-19T09:41:12Z
category: funcs
title: symmetricDifference
sha1: 942747445bc1be78b1e25c6c0a36522b26321f59
---

# symmetricDifference

## 语法

`symmetricDifference(X, Y)` 或
`X^Y`

## 详情

返回两个集合的并集减去两个集合的交集。

## 参数

**X** 和 **Y** 是集合。

## 返回值

一个集合。

## 例子

```dolphindb
x=set([5,3,4])
y=set(8 9 4 6);

y^x;
// output
set(5,8,3,9,6)

x^y;
// output
set(8,5,3,6,9)
```
