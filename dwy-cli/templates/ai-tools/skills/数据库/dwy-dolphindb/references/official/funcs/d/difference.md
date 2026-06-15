---
source_url: https://docs.dolphindb.cn/zh/funcs/d/difference.html
fetched_at: 2026-05-19T09:18:57Z
category: funcs
title: difference
sha1: f736e1d56bc8ec692cf18ad6b9d50361cf661b7f
---

# difference

## 语法

`difference(X)`

## 详情

返回向量的最后一个元素减第一个元素的值。如果 *X* 是一个标量，则返回 0。

## 参数

**X** 可以是标量或向量。

## 返回值

DOUBLE 类型标量。

## 例子

```dolphindb
difference(2 4 2);
// output
0

difference(12.3 15.6 17.8);
// output
5.5

difference(278);
// output
0
```
