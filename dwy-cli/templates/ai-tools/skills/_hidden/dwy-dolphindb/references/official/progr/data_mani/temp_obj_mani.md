---
source_url: https://docs.dolphindb.cn/zh/progr/data_mani/temp_obj_mani.html
fetched_at: 2026-05-19T09:02:18Z
category: progr
title: 时序对象的操作
sha1: 7a9c02b89eeea9a1165860c41b6c40a473d69ec3
---

# 时序对象的操作

## 获取时间变量的部分信息

获取时间变量的部分信息的用法如下：

```dolphindb
year(2016.02.14);
// output: 2016

monthOfYear(2016.02.14);
// output: 2

dayOfMonth(2016.02.14);
// output: 14

x=01:02:03.456;
hour(x);
// output: 1

minuteOfHour(x);
// output: 2

secondOfMinute(x);
// output: 3

x mod 1000;
// output: 456
```

## 用运算符调整时间变量值

使用运算符"+"或"-"来调整时间变量的值。

```dolphindb
2016.02M-13;
// output: 2015.01M

2018.02.17+100;
// output: 2018.05.28

01:20:15+200;
// output: 01:23:35
```

对于minute, second,
time和nanotime类型的时间序列对象，表示这些对象的内部整数的最小值为0，最大值分别为1440-1, 86400-1,
86400000-1和86400000000000-1。如果进行运算调整之后，其中一个表示这些对象的内部整数小于0或大于相应的最大值，最终结果是内部整数除以相应的最大值的余数。

```dolphindb
23:59m+10;
// output: 00:09m

00:00:01-2;
// output: 23:59:59

23:59:59.900+200;
// output: 00:00:00.100
```

## 用时间单位调整时间变量值

[temporalAdd](../../funcs/t/temporalAdd.html)
函数以不同的时间单位调整时间变量的值。

```dolphindb
temporalAdd(2017.01.16,1,"w");
// output: 2017.01.23

temporalAdd(2016.12M,2,"M");
// output: 2017.02M

temporalAdd(13:30m,-15,"m");
// output: 13:15m
```

## 合并日期与时间

[concatDateTime](../../funcs/c/concatDateTime.html) 函数可以合并日期和时间。

```dolphindb
concatDateTime(2019.06.15,13:25:10);
// output: 2019.06.15T13:25:10

concatDateTime(2019.06.15 2019.06.16 2019.06.17,[13:25:10, 13:25:12, 13:25:13]);
// output: [2019.06.15T13:25:10,2019.06.16T13:25:12,2019.06.17T13:25:13]
```

## 与 DateOffset 相关的函数

DolphinDB 提供了一系列函数，用于将日期调整到特定的周期边界（如月初、月末、工作日等）。这些函数的计算逻辑与 Python pandas 的 [DateOffset](https://pandas.pydata.org/docs/reference/offset_frequency.html) 保持一致。

**时间偏移计算规则**

**年度相关函数**

- [yearBegin](../../funcs/y/yearBegin.html)
  ：获取当年的第一天
- [yearEnd](../../funcs/y/yearEnd.html)
  ：获取当年的最后一天
- [businessYearBegin](../../funcs/b/businessYearBegin.html) ：获取当年的第一个工作日
- [businessYearEnd](../../funcs/b/businessYearEnd.html) ：获取当年的最后一个工作日
- [isYearStart](../../funcs/i/isYearStart.html) ：判断当天是否为年初第一天
- [isYearEnd](../../funcs/i/isYearEnd.html)
  ：判断当天是否为年末最后一天
- [isLeapYear](../../funcs/i/isLeapYear.html) ：判断当年是否为闰年

```dolphindb
yearBegin(2011.06.02);
// output: 2011.01.01

yearEnd(2011.06.02);
// output: 2011.12.31

businessYearBegin(2011.06.02);
// output: 2011.01.03

businessYearEnd(2011.06.12);
// output: 2011.12.30

isYearBegin(2011.01.01);
// output: true

isYearEnd(2011.12.31);
// output: true

isLeapYear(2012.06.25);
// output: true
```

**月度相关函数**

- [monthBegin](../../funcs/m/monthBegin.html) ：获取当月的第一天
- [monthEnd](../../funcs/m/monthEnd.html)
  ：获取当月的最后一天
- [businessMonthBegin](../../funcs/b/businessMonthBegin.html) ：获取当月的第一个工作日
- [businessMonthEnd](../../funcs/b/businessMonthEnd.html) ：获取当月的最后一个工作日
- [semiMonthBegin](../../funcs/s/semiMonthBegin.html) ：获取当月开始的第15（或其他）天
- [semiMonthEnd](../../funcs/s/semiMonthEnd.html) ：获取当月结束的第15（或其他）天
- [isMonthStart](../../funcs/i/isMonthStart.html) ：判断当天是否为月初的第一天
- [isMonthEnd](../../funcs/i/isMonthEnd.html) ：判断当天是否为月末的最后一天
- [daysInMonth](../../funcs/d/daysInMonth.html) ：获取当月的天数

```dolphindb
monthBegin(2016.12.06);
// output: 2016.12.01

monthEnd(2016.12.06);
// output: 2016.12.31

businessMonthBegin(2016.10.06);
// output: 2016.10.03

businessMonthEnd(2016.07.06);
// output: 2016.07.29

semiMonthBegin(2016.12.26);
// output: 2016.12.15

semiMonthEnd(2016.12.06,15);
// output: 2016.11.30

isMonthStart(2011.01.01);
// output: true

isMonthEnd(2011.12.31);
// output: true

daysInMonth(2012.12.02);
// output: 31
```

**季度与周相关函数**

- [quarterBegin](../../funcs/q/quarterBegin.html) ：获取当前季度的第一天
- [quarterEnd](../../funcs/q/quarterEnd.html) ：获取当前季度的最后一天
- [businessQuarterBegin](../../funcs/b/businessQuarterBegin.html) ：获取当前季度的第一个工作日
- [businessQuarterEnd](../../funcs/b/businessQuarterEnd.html) ：获取当前季度的最后一个工作日
- [isQuarterStart](../../funcs/i/isQuarterStart.html) ：判断当天是否为季度的第一天
- [isQuarterEnd](../../funcs/i/isQuarterEnd.html) ：判断当天是否为季度的最后一天

```dolphindb
quarterBegin(2012.06.12);
// output: 2012.04.01

quarterEnd(2012.06.12);
// output: 2012.06.30

businessQuarterBegin(2012.06.12);
// output: 2012.04.02

businessQuarterEnd(2012.06.12);
// output: 2012.06.29

isQuarterStart(2011.01.01);
// output: true

isQuarterEnd(2011.12.31);
// output: true
```

- [weekEnd](../../funcs/w/weekEnd.html)
  ：获取当前星期或下一个星期的星期几（默认为星期一）
- [weekBegin](../../funcs/w/weekBegin.html)
  ：获取当前星期或上一个星期的星期几（默认为星期一）
- [lastWeekOfMonth](../../funcs/l/lastWeekOfMonth.html) ：获取当月或上一个月最后一周的星期几（默认为星期一）
- [weekOfMonth](../../funcs/w/weekOfMonth.html) ：获取当月或上一个月第几周的星期几（默认为第一周的星期一）

```dolphindb
week(2019.11.24);
// output: 2019.11.25

weekBegin(2019.11.24);
// output: 2019.11.18

lastWeekOfMonth(2019.11.01);
// output: 2019.10.28

weekOfMonth(2019.11.01);
// output: 2019.10.07
```

- [fy5253](../../funcs/f/fy5253.html)
  ：获取当前财年开始的第一天
- [fy5253Quarter](../../funcs/f/fy5253Quarter.html) ：获取当前财季开始的第一天

```dolphindb
fy5253(2016.11.01);
// output: 2016.02.01

fy5253Quarter(2016.11.01);
// output: 2016.10.31
```

- [duration](../../funcs/d/duration.html)：设置一个时间区间。时间单位可以是常规时间单位或交易日历标识符。

```dolphindb
duration("5M")
// output: 5M

duration("3XNYS")
// output: 3XNYS
```
