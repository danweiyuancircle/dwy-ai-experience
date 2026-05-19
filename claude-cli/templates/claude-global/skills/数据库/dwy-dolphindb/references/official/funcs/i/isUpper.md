---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isUpper.html
fetched_at: 2026-05-19T09:28:57Z
category: funcs
title: isUpper
sha1: 26c29bce2b2d9d11f754314ecb33fe17f0f50945
---

# isUpper

## 语法

`isUpper(X)`

## 详情

判断字符串中的字母是否全部为大写。对于空字符串，该函数返回 false。

## 参数

**X** 是字符或字符串类型的标量或向量。

## 返回值

布尔标量或向量。

## 例子

```dolphindb
isUpper("THIS IS STRING EXAMPLE....WOW!!!");
// output: true

isUpper("THIS is string example....wow!!!");
// output: false

isUpper("123456ABC");
// output: true

isUpper("123");
// output: false

isUpper(["  ",string()]);
// output: [false,false]
```

相关函数：[isLower](isLower.html), [isTitle](isTitle.html)
