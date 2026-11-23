---
source_url: https://docs.dolphindb.cn/zh/funcs/t/trim.html
fetched_at: 2026-05-19T09:42:53Z
category: funcs
title: trim
sha1: f6ce3a476a80033e344e5bc6f62ce4db20a632b1
---

# trim

## 语法

`trim(X)`

## 详情

去掉每个字符串首尾的空格。

## 参数

**X** 是一个字符串标量或向量。

## 返回值

STRING 类型标量或向量。

## 例子

```dolphindb
x=["  t1", " t2 "];
trim(x);
// output
["t1","t2"]
```

相关函数：[strip](../s/strip.html)
