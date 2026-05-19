---
source_url: https://docs.dolphindb.cn/zh/funcs/m/memSize.html
fetched_at: 2026-05-19T09:31:33Z
category: funcs
title: memSize
sha1: 5170795cc32f9e72436f31126a759c905b4c2184
---

# memSize

## 语法

`memSize(obj)`

## 详情

返回本地对象或共享对象占用内存大小，单位为字节。

## 参数

**obj** 一个对象。

## 返回值

整型标量。

## 例子

```dolphindb
n=100
ID=rand(100, n)
date=rand(2017.08.07..2017.08.11, n)
x=rand(10.0, n)
t=table(ID, date, x);
share t as tt
memSize(t)
// output: 1952
memSize(tt)
// output: 1952
memSize(t[`x])
// output: 800
memSize(select avg(x) as avgx from t)
// output: 280
```

相关函数：[objs](../o/objs.html)
