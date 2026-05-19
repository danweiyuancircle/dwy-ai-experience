---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentpayofftype.html
fetched_at: 2026-05-19T09:24:32Z
category: funcs
title: getInstrumentPayoffType
sha1: ed7428b2e6ba622ad4c73c77ae04428314067fe8
---

# getInstrumentPayoffType

首发版本：3.00.4.1

## 语法

`getInstrumentPayoffType(instrument)`

## 详情

根据输入的金融工具，获取该工具的收益类型。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

STRING 类型标量或向量。

## 例子

```dolphindb
option = {
    "productType": "Option",
    "optionType": "EuropeanOption",
    "assetType": "FxEuropeanOption",
    "notionalCurrency": "EUR",
    "notionalAmount": 1000000.0,
    "strike": 1.2,
    "maturity": "2025.10.08",
    "payoffType": "Call",
    "dayCountConvention": "Actual365",
    "underlying": "EURUSD"
}
ins = parseInstrument(option)
getInstrumentPayoffType(ins)
// output: Call
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
