---
source_url: https://docs.dolphindb.cn/zh/funcs/s/strReplace.html
fetched_at: 2026-05-19T09:40:48Z
category: funcs
title: strReplace
sha1: 57116b3cd7675c4f60f62074c3049f889912e283
---

# strReplace

## 语法

`strReplace(str, pattern, replacement)`

## 详情

返回 *str* 的副本。如果 *str* 包含 *pattern*，则将
*pattern* 替换为 *replacement*。

## 参数

**str** 是目标字符串。它可以是标量或向量。

**pattern** 是被替换的字符串。

**replacement** 是替换的字符串。

## 返回值

STRING 类型标量或向量。

## 例子

```dolphindb
strReplace("The ball is red.", "red", "green");
// output
The ball is green.

strReplace(["The ball is red.", "The car is red too."], "red", "yellow");
// output
["The ball is yellow.","The car is yellow too."]
```
