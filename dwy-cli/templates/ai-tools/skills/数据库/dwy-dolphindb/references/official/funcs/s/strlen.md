---
source_url: https://docs.dolphindb.cn/zh/funcs/s/strlen.html
fetched_at: 2026-05-19T09:40:44Z
category: funcs
title: strlen
sha1: 34e0dc735213f8c05a1b2c42bd4fac49b0d0764c
---

# strlen

## 语法

`strlen(X)`

## 详情

获取目标字符串的长度。

## 参数

**X** 是目标字符串。它可以是标量或向量。

## 返回值

INT 类型标量或向量。

## 例子

```dolphindb
strlen('abcdefg');
// output
7

strlen("I am a boy.");
// output
11

strlen(["abc","123456789"]);
// output
[3,9]
```
