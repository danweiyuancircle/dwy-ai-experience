---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rtrim.html
fetched_at: 2026-05-19T09:37:43Z
category: funcs
title: rtrim
sha1: 402bcaf0d0204d8b95eb2e66ae4da0bcd2e911df
---

# rtrim

## 语法

`rtrim(X)`

## 详情

删除字符串或字符串向量的每个元素右边的空格。

## 参数

**X** 是一个字符串或字符串向量。

## 返回值

一个字符串或字符串向量。

## 例子

```dolphindb
rtrim("I love      ")+" "+ltrim("    this game!");
// output
I love this game!
```
