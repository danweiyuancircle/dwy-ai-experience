---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentexpiry.html
fetched_at: 2026-05-19T09:24:06Z
category: funcs
title: getInstrumentExpiry
sha1: 2596ccbfa85939e77445f9eb353d65a5bfdc111d
---

# getInstrumentExpiry

首发版本：3.00.4.1

## 语法

`getInstrumentExpiry(instrument)`

## 详情

根据输入的金融工具，获取该工具的到期日（Expiry Date）。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DATE 类型标量或向量。

## 例子

```dolphindb
forward =  {
   "productType": "Forward",
    "forwardType": "FxForward",
    "expiry": 2025.09.24,
    "delivery": 2025.09.26,
    "currencyPair": "USDCNY",
    "direction": "Buy",
    "notionalCurrency": "USD",
    "notionalAmount": 1E8,
    "strike": 7.2
}
ins = parseInstrument(forward)
getInstrumentExpiry(ins)

// Output: 2025.09.24
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
