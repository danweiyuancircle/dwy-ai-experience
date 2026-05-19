---
source_url: https://docs.dolphindb.cn/zh/funcs/u/undef.html
fetched_at: 2026-05-19T09:43:03Z
category: funcs
title: undef
sha1: 1a115e810e0f229d57d5bfb1f89b0644e1e9b6de
---

# undef

## 语法

`undef(obj, [objType=VAR])`

或

`undef all`

## 详情

从内存中释放变量和函数定义。VAR（本地变量）亦可通过 "= NULL" 释放变量。

## 参数

**obj** 需要取消定义的对象。如果想要取消所有变量、所有全局变量或所有用户自定义函数的定义，*obj* 可以使用 "all"。

**objType** 需要取消定义的对象的类型。可以是以下取值之一：VAR（本地变量）,SHARED（共享变量） 或 DEF（函数定义）。默认值是
VAR。

使用 `undef all` 删除系统中所有用户自定义的对象。

## 返回值

无。

## 例子

```dolphindb
undef all;
x=1
undef(`x);
x=1
y=2
undef(`x`y);
share table(1..3 as x, 4..6 as y) as t
undef(`t, SHARED);
```

```dolphindb
def f(a){return a+1}
undef(`f, DEF);
a=1
b=2
undef all, VAR;
// 取消所有变量的定义，但不包括函数定义。
```
