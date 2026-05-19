---
source_url: https://docs.dolphindb.cn/zh/funcs/s/secondOfMinute.html
fetched_at: 2026-05-19T09:38:10Z
category: funcs
title: secondOfMinute
sha1: 3274cfba25a75633ab10e0dd4a7271adbe720121
---

# secondOfMinute

## 语法

`secondOfMinute(X)`

## 详情

返回 *X* 中的秒数。

## 参数

**X** 可以是 TIME、SECOND、DATETIME、TIMESTAMP、NANOTIME 或
NANOTIMESTAMP 类型的标量或向量。

## 返回值

INT 类型标量或向量。

## 例子

```dolphindb
secondOfMinute(12:32:00);
// output
0

secondOfMinute([2012.06.12T12:30:00,2012.10.28T12:35:00,2013.01.06T12:36:47,2013.04.06T08:02:14]);
// output
[0,0,47,14]
```

相关函数：[dayOfYear](../d/dayOfYear.html), [dayOfMonth](../d/dayOfMonth.html), [quarterOfYear](../q/quarterOfYear.html), [monthOfYear](../m/monthOfYear.html), [weekOfYear](../w/weekOfYear.html), [hourOfDay](../h/hourOfDay.html), [minuteOfHour](../m/minuteOfHour.html), [millisecond](../m/millisecond.html), [microsecond](../m/microsecond.html), [nanosecond](../n/nanosecond.html)
