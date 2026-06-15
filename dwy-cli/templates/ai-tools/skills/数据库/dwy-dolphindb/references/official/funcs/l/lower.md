---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lower.html
fetched_at: 2026-05-19T09:30:30Z
category: funcs
title: lower
sha1: dffdb9cb97d91ecfb83ea347ed1bc0e1730ca539
---

# lower

## 语法

`lower(X)`

## 详情

`lower` 函数把字符串或字符串列表中的所有字符转换为小写。

当 *X* 是表时，函数仅作用于其中 CHAR、STRING、SYMBOL 列，其他类型的列将被忽略。

## 参数

**X** 是字符/字符串/SYMBOL 类型的标量、向量，或表。

## 返回值

返回值的类型和形式与 *X* 一致，所有字符均为小写。

## 例子

```dolphindb
x= `Ibm`C`AapL;
x.lower();
// output
["ibm","c","aapl"]

lower(`Thl);
// output
thl
```

相关函数：[upper](../u/upper.html)
