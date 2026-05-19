---
source_url: https://docs.dolphindb.cn/zh/funcs/l/listAllMarkets.html
fetched_at: 2026-05-19T09:29:44Z
category: funcs
title: listAllMarkets
sha1: a96bf3bf2fa73d93d34e9e122980b2b1260088e0
---

# listAllMarkets

首发版本：3.00.3

## 语法

`listAllMarkets()`

## 详情

获取当前节点所有的交易日历。

## 返回值

一个包含节点上所有交易日历标识的向量。

## 例子

```dolphindb
listAllMarkets()
// ["XTSE","XCSE","XLIM","ADDA","XSTO","XIST","AIXK","SSE","XMIL","XFRA","INE","XMEX","XBUD","XICE","XDUB","SHFE","CMES","XOSL","DCE","CCFX","CFFEX","XIDX","BVMF","XBOG","XKAR","XSAU","XBUE","XTKS","XBSE","XMOS"...]
```

**相关函数：**[addMarketHoliday](../a/addMarketHoliday.html)、[deleteMarketHoliday](../d/deleteMarketHoliday.html)
