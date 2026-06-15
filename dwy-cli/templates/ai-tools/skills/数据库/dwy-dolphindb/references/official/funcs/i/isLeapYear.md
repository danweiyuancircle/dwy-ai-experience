---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isLeapYear.html
fetched_at: 2026-05-19T09:28:30Z
category: funcs
title: isLeapYear
sha1: e5399bc18650431aeca080a652e77a20bac32516
---

# isLeapYear

## 语法

`isLeapYear(X)`

## 详情

判断 *X* 是否为闰年。

## 参数

**X** 可以是 DATE, DATEHOUR, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

布尔标量或向量。

## 例子

```dolphindb
isLeapYear(2012.06.12T12:30:00);
// output: true

isLeapYear([2012.01.01,2013.01.01,2014.01.01,2015.01.01]);
// output: [true,false,false,false]
```
