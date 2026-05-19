---
source_url: https://docs.dolphindb.cn/zh/funcs/w/wc.html
fetched_at: 2026-05-19T09:43:50Z
category: funcs
title: wc
sha1: 2b0a2f5983bf36583a7f78f9af97d268e8e6cd00
---

# wc

## 语法

`wc(X)`

## 详情

计算 *X* 中包含的单词数量。

## 参数

**X** 是一个字符串。它可以是标量或向量。

## 返回值

一个 INT 类型的标量或向量。

## 例子

```dolphindb
wc(`apple);
// output
1

wc("This is a 7th generation iphone!");
// output
6

wc("This is a 7th generation iphone!" "I wonder what the 8th generation looks like");
// output
[6,8]
```
