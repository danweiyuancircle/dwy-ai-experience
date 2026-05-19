---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isYearStart.html
fetched_at: 2026-05-19T09:29:03Z
category: funcs
title: isYearStart
sha1: ee4c6eb2eb9b26f5bde7191535982ef21ba30e7f
---

# isYearStart

## 语法

`isYearStart(X)`

## 详情

判断 *X* 是否为年初第一天。

## 参数

**X** 可以是 DATE, DATEHOUR, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

布尔标量或向量。

## 例子

```dolphindb
isYearStart(2012.01.01);
// output: true

isYearStart([2012.01.01,2012.02.01]);
// output: [true,false]
```

相关函数：[isYearEnd](isYearEnd.html)
