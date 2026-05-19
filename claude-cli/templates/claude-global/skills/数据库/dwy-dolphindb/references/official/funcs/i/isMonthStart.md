---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isMonthStart.html
fetched_at: 2026-05-19T09:28:38Z
category: funcs
title: isMonthStart
sha1: 9a9d1826528901e4a3161be3b3d94104ac4c84d2
---

# isMonthStart

## 语法

`isMonthStart(X)`

## 详情

判断 *X* 是否为月初第一天。

## 参数

**X** 可以是 DATE, DATEHOUR, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

布尔型标量或向量。

## 例子

```dolphindb
isMonthStart(2012.05.01);
// output: true

isMonthStart([2012.05.01,2012.05.02]);
// output: [true,false]
```

相关函数：[isMonthEnd](isMonthEnd.html)
