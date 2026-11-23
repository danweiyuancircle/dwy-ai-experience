---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isLoggedIn.html
fetched_at: 2026-05-19T09:28:32Z
category: funcs
title: isLoggedIn
sha1: 69697cce542ba720bef581c4b83b591897b5d29e
---

# isLoggedIn

## 语法

`isLoggedIn(userId)`

## 详情

检查用户是否已经登录。

## 参数

**userId** 是表示用户名的字符串。它只能包含字母、数字和下划线。它不能以数字开头，长度不能超过30个字符。

## 返回值

返回一个布尔值。

## 例子

```dolphindb
isLoggedIn(`AlexSmith)
// output: false
```
