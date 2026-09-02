---
source_url: https://docs.dolphindb.cn/zh/funcs/m/monthOfYear.html
fetched_at: 2026-05-19T09:32:21Z
category: funcs
title: monthOfYear
sha1: 723b7118f33ac3d2df9039b8b2345de5d660cfc0
---

# monthOfYear

## 语法

`monthOfYear(X)`

## 详情

返回 *X* 中的月份。

## 参数

**X** 可以是 DATE, MONTH, DATETIME, TIMESTAMP 或 NANOTIMESTAMP 类型的标量、向量或表。

## 返回值

整型标量或向量。

## 例子

```dolphindb
monthOfYear(2012.07.02);
// output: 7

monthOfYear([2012.06.12T12:30:00,2012.10.28T12:35:00,2013.01.06T12:36:47,2013.04.06T08:02:14]);
// output: [6,10,1,4]
```

相关函数：[dayOfYear](../d/dayOfYear.html), [dayOfMonth](../d/dayOfMonth.html), [quarterOfYear](../q/quarterOfYear.html), [weekOfYear](../w/weekOfYear.html), [hourOfDay](../h/hourOfDay.html), [minuteOfHour](minuteOfHour.html), [secondOfMinute](../s/secondOfMinute.html), [millisecond](millisecond.html), [microsecond](microsecond.html), [nanosecond](../n/nanosecond.html)
