---
source_url: https://docs.dolphindb.cn/zh/funcs/g/gettradingcalendartype.html
fetched_at: 2026-05-19T09:26:31Z
category: funcs
title: getTradingCalendarType
sha1: 2e5789ee58ea8591392a4244a42097b096e5e4ba
---

# getTradingCalendarType

## 语法

`getTradingCalendarType(marketName)`

## 详情

获取指定交易所对应的交易日历的类型。返回值是字符串标量，为 "holidayDate" 或 "tradingDate"。

## 参数

**marketName** 字符串标量，表示交易日历标识，例如：国外交易所的 ISO Code、国内交易所简称或自定义交易日历名称。

## 返回值

字符串标量，为 "holidayDate" 或 "tradingDate"。

## 例子

运行以下命令获取交易日历类型：

```dolphindb
getTradingCalendarType("SZSE")
```

返回：holidayDate
