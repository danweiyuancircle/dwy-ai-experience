---
source_url: https://docs.dolphindb.cn/zh/funcs/d/daysInMonth.html
fetched_at: 2026-05-19T09:18:18Z
category: funcs
title: daysInMonth
sha1: e3948171a21a9f17b42da1fe74e2e072e10e8f81
---

# daysInMonth

## 语法

`daysInMonth(X)`

## 详情

返回 *X* 所在月份的天数。

## 参数

**X** 可以是 DATE, DATEHOUR, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

整数类型的标量或向量。

## 例子

```dolphindb
daysInMonth(2012.06.12T12:30:00);
// output
30

daysInMonth([2012.02.01,2013.12.05]);
// output
[29,31]
```
