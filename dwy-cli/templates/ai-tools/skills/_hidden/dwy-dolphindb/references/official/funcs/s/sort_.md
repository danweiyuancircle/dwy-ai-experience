---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sort_.html
fetched_at: 2026-05-19T09:39:36Z
category: funcs
title: sort!
sha1: 319d61ff79cc1e4806fefe2c35615c9ef3df92af
---

# sort!

## 语法

`sort!(X, [ascending=true])`

## 详情

对向量/矩阵进行排序。该函数会改变 *X* 的值。

## 参数

**X** 是一个向量/向量。

**ascending** 是一个布尔值，表示按升序排序还是按降序排序。默认值为 true（按升序排序）。

## 返回值

返回排序后的向量/矩阵。

## 例子

```dolphindb
x=9 1 5;
sort!(x);
x;
// output
[1 5 9]

x.sort!(0);
x;
// output
[9,5,1]
```
