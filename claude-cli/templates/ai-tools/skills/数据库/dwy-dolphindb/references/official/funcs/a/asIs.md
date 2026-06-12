---
source_url: https://docs.dolphindb.cn/zh/funcs/a/asIs.html
fetched_at: 2026-05-19T09:13:18Z
category: funcs
title: asis
sha1: 490d6545d826a8aefec7e47223d5a7ff9d2d5b45
---

# asis

## 语法

`asis(obj)`

## 详情

返回 *obj* 的引用。

## 参数

**obj** 可以是任意数据类型。

## 返回值

数据类型与数据形式与 *obj* 相同。

## 例子

```dolphindb
a = 1 2 3
b = asis(a)
a[0] = 0
b
// output
[0, 2, 3]
b[1] = 4
// output
a;
[0, 4, 3]
```

相关函数：[copy](../c/copy.html), [deepCopy](../d/deepCopy.html)
