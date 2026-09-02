---
source_url: https://docs.dolphindb.cn/zh/funcs/p/pair.html
fetched_at: 2026-05-19T09:33:46Z
category: funcs
title: pair
sha1: 973d00ce7c449e438f3d2f621b26801a5f27f272
---

# pair

## 语法

`pair(a, b)` 或 `a:b`

## 详情

返回一个数据对。

## 参数

**a** 和 **b** 必须是标量。

## 返回值

数据对标量，类型同 *a*/*b*。

## 例子

```dolphindb
1:3+1;
// output: 2:4

1:3<0:6;
// output: 0 : 1
```
