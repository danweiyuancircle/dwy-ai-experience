---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isSorted.html
fetched_at: 2026-05-19T09:28:53Z
category: funcs
title: isSorted
sha1: 71a10d4a54f22e89a3081c652c2ea343d660e7a8
---

# isSorted

## 语法

`isSorted(X, [ascending=true])`

## 详情

检查 *X* 是否有序。

## 参数

**X** 是一个向量。

**ascending** 是布尔值，表示 *X* 按升序排序（true）或降序排序（false）。默认值为 true。

## 返回值

布尔标量。

## 例子

```dolphindb
x=NULL 1 2 3
isSorted(x);
// output: true

t=table(9 7 5 3 as x, 1 5 2 4 as y)
t.x.isSorted(false);
// output: true

t.y.isSorted();
// output: false
```
