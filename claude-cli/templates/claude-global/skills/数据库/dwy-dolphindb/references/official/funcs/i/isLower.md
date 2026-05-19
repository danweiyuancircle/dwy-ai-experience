---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isLower.html
fetched_at: 2026-05-19T09:28:33Z
category: funcs
title: isLower
sha1: b98c832d86ba805f2eecc1080b47f4b9ff5102ac
---

# isLower

## 语法

`isLower(X)`

## 详情

判断字符串中的字母是否全部为小写。对于空字符串，该函数返回 false。

## 参数

**X** 是字符或字符串类型的标量、向量或表。

## 返回值

- 当 *X* 是标量时，返回布尔标量。
- 当 *X* 是向量时，返回布尔向量。
- 当 *X* 是表时，返回一个表。

## 例子

```dolphindb
isLower("this is string example....wow!!!");
// output: true

isLower("THIS is string example....wow!!!");
// output: false

isLower("123456abc");
// output: true

isLower("123");
// output: false

isLower(["  ",string()]);
// output: [false,false]
```

相关函数：[isUpper](isUpper.html), [isTitle](isTitle.html)
