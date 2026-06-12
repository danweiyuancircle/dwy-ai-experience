---
source_url: https://docs.dolphindb.cn/zh/funcs/s/startsWith.html
fetched_at: 2026-05-19T09:40:01Z
category: funcs
title: startsWith
sha1: aad0b94a3dec3388f75ada5ba0e1d6e69f97b1e4
---

# startsWith

## 语法

`startsWith(X, str)`

## 详情

检查 *X* 是否以 *str* 开头。如果是，返回 true； 否则返回 false。

## 参数

**X** 是在该字符串中搜索。它可以是标量或向量。

**str** 是被搜索的目标字符串。它必须是标量。

## 返回值

一个布尔值。

## 例子

```dolphindb
str1="US product"
str2="UK product"
if (startsWith(str1, "US")) print "str1 is a US product."
else print "str1 is not a US product."
if (startsWith(str2, "US")) print "str2 is a US product."
else print "str2 is not a US product.";

// output
str1 is a US product.
str2 is not a US product.
```
