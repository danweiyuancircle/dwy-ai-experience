---
source_url: https://docs.dolphindb.cn/zh/funcs/s/set.html
fetched_at: 2026-05-19T09:38:23Z
category: funcs
title: set
sha1: afb7f63be90a85531c0cb2de23e61d0df80739a6
---

# set

## 语法

`set(X)`

## 详情

返回向量 *X* 对应的集合对象。

## 参数

**X** 是一个向量。

## 返回值

返回向量 X 对应的集合对象。

## 例子

`set` 函数返回一个集合。

```dolphindb
x=set(4 5 5 2 3 11 6);
x;
// output
set(6,11,3,2,5,4)

x.intersection(set([2,5,9]));
// output
set(2,5)
```

与此不同，[distinct](../d/distinct.html) 函数返回一个向量。

```dolphindb
distinct(4 5 5 2 3 11 6);
// output
[6,11,3,2,5,4]
```
