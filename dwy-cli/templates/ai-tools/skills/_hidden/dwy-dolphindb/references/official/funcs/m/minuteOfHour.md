---
source_url: https://docs.dolphindb.cn/zh/funcs/m/minuteOfHour.html
fetched_at: 2026-05-19T09:31:58Z
category: funcs
title: minuteOfHour
sha1: 2ee58e312d124c3f037d3f3dc103cd6b97a56e04
---

# minuteOfHour

## 语法

`minuteOfHour(X)`

## 详情

返回 *X* 中的分钟数。

## 参数

**X** 可以是 TIME, MINUTE, SECOND, DATETIME, TIMESTAMP, NANOTIME 或
NANOTIMESTAMP 类型的标量或向量。

## 返回值

整型标量或向量。

## 例子

```dolphindb
minuteOfHour(12:32:00);
// output: 32

minuteOfHour([2012.06.12T12:30:00,2012.10.28T12:35:00,2013.01.06T12:36:47,2013.04.06T08:02:14]);
// output: [30,35,36,2]
```

相关函数：[dayOfYear](../d/dayOfYear.html), [dayOfMonth](../d/dayOfMonth.html), [quarterOfYear](../q/quarterOfYear.html), [monthOfYear](monthOfYear.html), [weekOfYear](../w/weekOfYear.html), [hourOfDay](../h/hourOfDay.html), [secondOfMinute](../s/secondOfMinute.html), [millisecond](millisecond.html), [microsecond](microsecond.html), [nanosecond](../n/nanosecond.html)
