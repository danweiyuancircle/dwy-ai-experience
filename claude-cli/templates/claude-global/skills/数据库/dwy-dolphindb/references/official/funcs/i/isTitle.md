---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isTitle.html
fetched_at: 2026-05-19T09:28:55Z
category: funcs
title: isTitle
sha1: 38f7fab6e23db42d07c61f78d2a71f9e856be909
---

# isTitle

## 语法

`isTitle(X)`

## 详情

判断字符串中每个单词的第一个字母是否为大写，其他字母都为小写。对于不包含字母的字符串和空字符串，该函数返回 false。

## 参数

**X** 可以是字符串标量或向量。

## 返回值

布尔标量或向量。

## 例子

```dolphindb
isTitle("Hello World");
// output: true

isTitle("Hello world");
// output: false

isTitle(["Hello","468","  "]);
// output: [true,false,false]

isTitle("1And1");
// output: true
```

相关函数：[isLower](isLower.html), [isUpper](isUpper.html)
