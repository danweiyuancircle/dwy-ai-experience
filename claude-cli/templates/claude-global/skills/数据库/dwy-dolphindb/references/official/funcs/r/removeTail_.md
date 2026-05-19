---
source_url: https://docs.dolphindb.cn/zh/funcs/r/removeTail_.html
fetched_at: 2026-05-19T09:35:47Z
category: funcs
title: removeTail!
sha1: 79ad700b97a5b44995442801866c73501b692033
---

# removeTail!

## 语法

`removeTail!(obj, n)`

## 详情

删除向量 *obj* 的后 *n* 个元素。

## 参数

**obj** 是一个向量。

**n** 是一个正整数，表示要删除的位于向量尾部的元素的个数。

## 返回值

与 *obj* 同类型的向量。

## 例子

```dolphindb
x=11..20;
x.removeTail!(3);
// output
[11,12,13,14,15,16,17]
```

**相关函数：**[drop](../d/drop.html)、[pop!](../p/pop_.html)、[removeHead!](removeHead_.html)、[remove!](remove.html)
