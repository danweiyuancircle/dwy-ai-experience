---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentfardelivery.html
fetched_at: 2026-05-19T09:24:07Z
category: funcs
title: getInstrumentFarDelivery
sha1: ba7801f3c40e6f6e7e6a2d3d45b88b8b4b6f8d1f
---

# getInstrumentFarDelivery

首发版本：3.00.4.1

## 语法

`getInstrumentFarDelivery(instrument)`

## 详情

根据输入的金融工具，获取该工具的远端交割日期（far delivery date）。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DATE 类型标量或向量。

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
ins = parseInstrument(swap)
getInstrumentFarDelivery(ins)

// output: 2026.06.10
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
