---
source_url: https://docs.dolphindb.cn/zh/funcs/h/hourOfDay.html
fetched_at: 2026-05-19T09:27:23Z
category: funcs
title: hourOfDay
sha1: 105edb0ffd2ea384b2d895a5bdea48ee965a715f
---

# hourOfDay

## 语法

`hourOfDay(X)`

## 详情

返回 *X* 中的小时。

## 参数

**X** 可以是 TIME, MINUTE, SECOND, DATETIME, TIMESTAMP, NANOTIME,
NANOTIMESTAMP 类型的标量或向量。

## 返回值

INT 类型标量或向量。

## 例子

```dolphindb
hourOfDay(00:46:12);
// output
0

hourOfDay([2012.06.12T12:30:00,2012.10.28T17:35:00,2013.01.06T02:36:47,2013.04.06T08:02:14]);
// output
[12,17,2,8]
```

相关函数：[dayOfYear](../d/dayOfYear.html), [dayOfMonth](../d/dayOfMonth.html), [quarterOfYear](../q/quarterOfYear.html), [monthOfYear](../m/monthOfYear.html), [weekOfYear](../w/weekOfYear.html), [minuteOfHour](../m/minuteOfHour.html), [secondOfMinute](../s/secondOfMinute.html), [millisecond](../m/millisecond.html), [microsecond](../m/microsecond.html), [nanosecond](../n/nanosecond.html)
