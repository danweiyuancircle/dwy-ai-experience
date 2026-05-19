---
source_url: https://docs.dolphindb.cn/zh/funcs/q/quarterOfYear.html
fetched_at: 2026-05-19T09:34:50Z
category: funcs
title: quarterOfYear
sha1: b9a49b372c5c8e3a750b7c277e37a13910432921
---

# quarterOfYear

## 语法

`quarterOfYear(X)`

## 详情

计算X在当年的第几个季度。返回的结果是整型。

## 参数

**X** 可以是 DATE, MONTH, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

整型标量或向量。

## 例子

```dolphindb
quarterOfYear(2012.07.02);
// output
3

quarterOfYear([2012.06.12T12:30:00,2012.10.28T12:35:00,2013.01.06T12:36:47,2013.04.06T08:02:14]);
// output
[2,4,1,2]
```

相关函数：[dayOfYear](../d/dayOfYear.html), [dayOfMonth](../d/dayOfMonth.html), [monthOfYear](../m/monthOfYear.html), [weekOfYear](../w/weekOfYear.html), [hourOfDay](../h/hourOfDay.html), [minuteOfHour](../m/minuteOfHour.html), [secondOfMinute](../s/secondOfMinute.html), [millisecond](../m/millisecond.html), [microsecond](../m/microsecond.html), [nanosecond](../n/nanosecond.html)
