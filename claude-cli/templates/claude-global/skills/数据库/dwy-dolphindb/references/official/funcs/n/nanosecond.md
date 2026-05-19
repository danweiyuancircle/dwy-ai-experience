---
source_url: https://docs.dolphindb.cn/zh/funcs/n/nanosecond.html
fetched_at: 2026-05-19T09:33:06Z
category: funcs
title: nanosecond
sha1: a9f9c753fb38a9b58dc0ab6ccf03678b7bc218ec
---

# nanosecond

## 语法

`nanosecond(X)`

## 详情

返回 *X* 中的纳秒数。

## 参数

**X** 可以是 TIME, TIMESTAMP, NANOTIME 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

INT 类型标量或向量。

## 例子

```dolphindb
nanosecond(13:30:10.008);
// output
8000000

nanosecond([2012.12.03 01:22:01.999999999, 2012.12.03 01:25:08.000000234]);
// output
[999999999,234]
```

相关函数：[dayOfYear](../d/dayOfYear.html), [dayOfMonth](../d/dayOfMonth.html), [quarterOfYear](../q/quarterOfYear.html), [monthOfYear](../m/monthOfYear.html), [weekOfYear](../w/weekOfYear.html), [hourOfDay](../h/hourOfDay.html), [minuteOfHour](../m/minuteOfHour.html), [secondOfMinute](../s/secondOfMinute.html), [millisecond](../m/millisecond.html), [microsecond](../m/microsecond.html)
