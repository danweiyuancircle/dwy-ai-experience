---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getInstrumentFarStrike.html
fetched_at: 2026-05-19T09:24:10Z
category: funcs
title: getInstrumentFarStrike
sha1: 90bf80f8b350a8550896ecea7e3ca082b197c730
---

# getInstrumentFarStrike

首发版本：3.00.4.1

## 语法

`getInstrumentFarStrike(instrument)`

## 详情

根据输入的金融工具，获取该工具的远端行权价格。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
swap = {
    "productType": "Swap",
    "swapType": "FxSwap",
    "currencyPair": "EURUSD",
    "direction": "Buy",
    "notionalCurrency": "EUR",
    "notionalAmount": 1E6,
    "nearStrike": 1.1,
    "nearExpiry": 2025.12.08,
    "nearDelivery": 2025.12.10,
    "farStrike": 1.2,
    "farExpiry": 2026.06.08,
    "farDelivery": 2026.06.10
}
instrument = parseInstrument(swap)
getInstrumentFarStrike(instrument)

// output: 1.2
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
