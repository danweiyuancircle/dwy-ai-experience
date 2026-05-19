---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentfarexpiry.html
fetched_at: 2026-05-19T09:24:09Z
category: funcs
title: getInstrumentFarExpiry
sha1: 7243180b0b6e33d54956e238d28e5c0441c35286
---

# getInstrumentFarExpiry

首发版本：3.00.4.1

## 语法

`getInstrumentFarExpiry(instrument)`

## 详情

根据输入的金融工具，获取该工具的远端到期日（far expiry date）。

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
getInstrumentFarExpiry(ins)

// output: 2026.06.08
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
