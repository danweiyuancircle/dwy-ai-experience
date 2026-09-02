---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentnearstrike.html
fetched_at: 2026-05-19T09:24:25Z
category: funcs
title: getInstrumentNearStrike
sha1: ab26375716eb02c887819728d0df913def93b7de
---

# getInstrumentNearStrike

首发版本：3.00.4.1

## 语法

`getInstrumentNearStrike(instrument)`

## 详情

根据输入的金融工具，获取该工具的近端行权价格。

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

getInstrumentNearStrike(instrument)
// output: 1.1
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
