---
source_url: https://docs.dolphindb.cn/zh/funcs/p/partial.html
fetched_at: 2026-05-19T09:33:56Z
category: funcs
title: partial
sha1: cccf7950a069c792d7598411145133fcdd8a3c3e
---

# partial

## 语法

`partial(func, args...)`

## 详情

创建一个部分应用。

## 参数

**func** 是 DolphinDB 中的函数。

**args...** 是函数的参数。

## 返回值

一个 FUNCTIONDEF。

## 例子

```dolphindb
partial(add,1)(2);
// output
3

def f(a,b):a pow b
g=partial(f, 2)
g(3);
// output
8
```
