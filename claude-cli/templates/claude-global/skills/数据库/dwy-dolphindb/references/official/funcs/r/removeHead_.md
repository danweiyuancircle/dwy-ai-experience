---
source_url: https://docs.dolphindb.cn/zh/funcs/r/removeHead_.html
fetched_at: 2026-05-19T09:35:44Z
category: funcs
title: removeHead!
sha1: c5333d008ea33f5cca5255b130d3d005608cb4be
---

# removeHead!

## 语法

`removeHead!(obj, n)`

## 详情

删除向量 *obj* 的前 *n* 个元素。

## 参数

**obj** 是一个向量。

**n** 是一个正整数，表示要删除的位于向量头部的元素的个数。

## 返回值

与 *obj* 同类型的向量。

## 例子

```dolphindb
x=11..20;
x.removeHead!(3);
// output
[14,15,16,17,18,19,20]
```

**相关函数：**[drop](../d/drop.html)、[pop!](../p/pop_.html)、[removeTail!](removeTail_.html)、[remove!](remove.html)
