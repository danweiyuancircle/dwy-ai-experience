---
source_url: https://docs.dolphindb.cn/zh/funcs/p/pop_.html
fetched_at: 2026-05-19T09:34:23Z
category: funcs
title: pop!
sha1: 843ddf92d9267b25287f770cbb0fb6eb80cb6f7a
---

# pop!

## 语法

`pop!(X)`

## 详情

移除 *X* 中的最后一个元素。

## 参数

**X** 是一个向量。

## 返回值

一个标量，类型同 *X*，表示被移除的元素。

## 例子

```dolphindb
x = 1 2 3;
pop!(x);
// output
3

x;
// output
[1,2]
```

**相关函数：**[drop](../d/drop.html)、[removeHead!](../r/removeHead_.html)、[removeTail!](../r/removeTail_.html)、[remove!](../r/remove.html)
