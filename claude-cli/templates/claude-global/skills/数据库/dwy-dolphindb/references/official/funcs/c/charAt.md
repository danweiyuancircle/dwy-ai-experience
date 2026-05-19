---
source_url: https://docs.dolphindb.cn/zh/funcs/c/charAt.html
fetched_at: 2026-05-19T09:14:59Z
category: funcs
title: charAt
sha1: 5c00bd54d4236d7384590813090d7566773c2a5a
---

# charAt

## 语法

`charAt(X, Y)`

## 详情

返回字符串中指定位置的字符。返回的结果是 CHAR 类型。

## 参数

**X** 是字符串标量或向量。

**Y** 是整型标量或与 *X* 长度相同的整型向量。

## 返回值

CHAR 类型标量或向量。

## 例子

```dolphindb
s=charAt("abc",2);
s;
// output
'c'

typestr(s);
// output
CHAR

charAt(["hello","world"],[3,4]);
// output
['l','d']
```
