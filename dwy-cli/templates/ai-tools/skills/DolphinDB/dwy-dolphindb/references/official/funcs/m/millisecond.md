---
source_url: https://docs.dolphindb.cn/zh/funcs/m/millisecond.html
fetched_at: 2026-05-19T09:31:47Z
category: funcs
title: millisecond
sha1: 29f12160de7028ac4e04b0a5abc65c12c8fd406d
---

# millisecond

## 语法

`millisecond(X)`

## 详情

返回 *X* 中的毫秒数。

## 参数

**X** 可以是 TIME, TIMESTAMP, NANOTIME 或 NANOTIMESTAMP
类型的标量或向量。

## 返回值

整型标量或向量。

## 例子

```dolphindb
millisecond(13:30:10.008);
// output: 8

millisecond([2012.12.03 01:22:01.456120300, 2012.12.03 01:25:08.000234000]);
// output: [456,0]
```

相关函数：[dayOfYear](../d/dayOfYear.html), [dayOfMonth](../d/dayOfMonth.html), [quarterOfYear](../q/quarterOfYear.html), [monthOfYear](monthOfYear.html), [weekOfYear](../w/weekOfYear.html), [hourOfDay](../h/hourOfDay.html), [minuteOfHour](minuteOfHour.html), [secondOfMinute](../s/secondOfMinute.html), [microsecond](microsecond.html), [nanosecond](../n/nanosecond.html)
