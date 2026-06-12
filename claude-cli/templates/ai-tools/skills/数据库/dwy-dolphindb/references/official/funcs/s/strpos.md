---
source_url: https://docs.dolphindb.cn/zh/funcs/s/strpos.html
fetched_at: 2026-05-19T09:40:46Z
category: funcs
title: strpos
sha1: ee87ebfb9002882d5fc1a90e532770d76d528da7
---

# strpos

## 语法

`strpos(X, str)`

别名：strFind

## 详情

检查 *X* 是否包含 *str*。

## 参数

**X** 是在该字符串中搜索。它可以是标量或向量。

**str** 是被搜索的目标字符串。它可以是标量或向量。

## 返回值

如果 X 中包含 str，返回 str 在 X 中的起始位置； 否则返回-1。

## 例子

```dolphindb
strpos("abcdefg","cd");
// output
2

strpos("abcdefg","d");
// output
3

strpos("abcdefg","ah");
// output
-1
```
