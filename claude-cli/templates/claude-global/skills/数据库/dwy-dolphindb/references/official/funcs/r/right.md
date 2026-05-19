---
source_url: https://docs.dolphindb.cn/zh/funcs/r/right.html
fetched_at: 2026-05-19T09:36:33Z
category: funcs
title: right
sha1: 12e08437e18bc307b49d7869ba10ba0432c8b03b
---

# right

## 语法

`right(X, n)`

## 详情

返回 *X* 右边 *n* 个字符。

## 参数

**X** 是一个字符串或字符串向量。

**n** 必须是一个非负整数。

## 返回值

返回一个字符串或字符串向量。

## 例子

```dolphindb
right("I love this game!", 6);
```

输出返回：game!
