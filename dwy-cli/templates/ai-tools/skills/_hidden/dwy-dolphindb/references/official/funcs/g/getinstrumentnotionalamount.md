---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentnotionalamount.html
fetched_at: 2026-05-19T09:24:28Z
category: funcs
title: getInstrumentNotionalAmount
sha1: 41cda5d95d90057d6811c6f65bb5430e6f63b5e7
---

# getInstrumentNotionalAmount

首发版本：3.00.4.3

## 语法

`getInstrumentNotionalAmount(instrument)`

## 详情

根据输入的金融工具，获取该工具的名义本金金额。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
deposit =  {
    "productType": "Cash",
    "assetType": "Deposit",
    "start": 2025.05.15,
    "maturity": 2025.08.15,
    "rate": 0.02,
    "dayCountConvention": "Actual360",
    "notionalAmount":1E6,
    "notionalCurrency":"CNY",
    "payReceive": "Receive"
}
instrument = parseInstrument(deposit)
getInstrumentNotionalAmount(instrument)

// output: 1000000
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)、[getInstrumentNotionalCurrency](getinstrumentnotionalcurrency.html)
