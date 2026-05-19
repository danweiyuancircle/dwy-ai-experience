---
source_url: https://docs.dolphindb.cn/zh/funcs/l/left.html
fetched_at: 2026-05-19T09:29:34Z
category: funcs
title: left
sha1: f77aafe77aadc84ddcfdb5ec40c7b34407df0eb6
---

# left

## 语法

`left(X,n)`

## 详情

返回 *X* 左边 *n* 个字符。

当 *X* 是表时，函数仅作用于其中字符串列，其他类型的列将被忽略。

## 参数

**X** 是字符串类型的标量、向量，或表。

**n** 必须是一个非负整数。

## 返回值

返回值的类型和形式与 *X* 保持一致。

## 例子

返回左边的6个字符（包含空格）。

```dolphindb
left("I love this game!", 6);
// output
I love
```
