---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentnearexpiry.html
fetched_at: 2026-05-19T09:24:24Z
category: funcs
title: getInstrumentNearExpiry
sha1: 8f0999a6b9cb8e17b8986ead5c13335312bd490f
---

# getInstrumentNearExpiry

首发版本：3.00.4.1

## 语法

`getInstrumentNearExpiry(instrument)`

## 详情

根据输入的金融工具，获取该工具的近端到期日（near expiry date）。

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
getInstrumentNearExpiry(ins)

// output: 2025.12.08
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
