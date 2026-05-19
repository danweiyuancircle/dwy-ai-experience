---
source_url: https://docs.dolphindb.cn/zh/funcs/r/refCount.html
fetched_at: 2026-05-19T09:35:29Z
category: funcs
title: refCount
sha1: 777ea638da498199e574a9b82c9c95f9ea1a20b1
---

# refCount

## 语法

`refCount(varname)`

## 详情

计算某个对象被引用的数量。

## 参数

**varname** 是一个字符串，表示变量名称。

## 返回值

INT 类型标量。

## 例子

```dolphindb
db=database("",VALUE,1 2 3)
refCount(`db);
// output
1

db1=db
db2=db
refCount(`db);
// output
3
```
