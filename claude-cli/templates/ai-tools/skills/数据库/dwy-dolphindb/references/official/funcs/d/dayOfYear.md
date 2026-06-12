---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dayOfYear.html
fetched_at: 2026-05-19T09:18:17Z
category: funcs
title: dayOfYear
sha1: 1e3a06ddc81ceb64b2807a800da2908fe9d781da
---

# dayOfYear

## 语法

`dayOfYear(X)`

## 详情

计算 *X* 是当年中的第几天。返回的结果是整型。

## 参数

**X** 可以是 DATE, DATETIME, TIMESTAMP 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

整数类型的标量或向量。

## 例子

```dolphindb
dayOfYear(2011.01.01);
// output
1

dayOfYear([2011.12.31,2012.12.31]);
// output
[365,366]

dayOfYear([2012.06.12T12:30:00,2012.07.12T12:35:00]);
// output
[164,194]
```

相关函数：[dayOfMonth](dayOfMonth.html), [quarterOfYear](../q/quarterOfYear.html), [monthOfYear](../m/monthOfYear.html), [weekOfYear](../w/weekOfYear.html), [hourOfDay](../h/hourOfDay.html), [minuteOfHour](../m/minuteOfHour.html), [secondOfMinute](../s/secondOfMinute.html), [millisecond](../m/millisecond.html), [microsecond](../m/microsecond.html), [nanosecond](../n/nanosecond.html)
