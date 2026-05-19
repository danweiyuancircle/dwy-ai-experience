---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentfixeddaycountconvention.html
fetched_at: 2026-05-19T09:24:12Z
category: funcs
title: getInstrumentFixedDayCountConvention
sha1: 09f752c34cd838fdc05a81481d9a76ea7a91beb1
---

# getInstrumentFixedDayCountConvention

首发版本：3.00.4.1

## 语法

`getInstrumentFixedDayCountConvention(instrument)`

## 详情

根据输入的金融工具，获取该工具的固定端日期计数惯例。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

STRING 类型标量或向量。

## 例子

```dolphindb
swap =  {
    "productType": "Swap",
    "swapType": "IrSwap",
    "irSwapType": "IrFixedFloatingSwap",
    "start": 2021.05.15,
    "maturity": 2023.05.15,
    "frequency": "Quarterly",
    "fixedRate": 0.02,
    "calendar": "CFET", 
    "fixedDayCountConvention": "Actual365",
    "floatingDayCountConvention": "Actual360",
    "payReceive": "Pay",
    "iborIndex": "SHIBOR_3M",
    "spread": 0.0005,
    "notionalCurrency": "CNY",
    "notionalAmount": 1E8
}
instrument = parseInstrument(swap)
getInstrumentFixedDayCountConvention(instrument)

// output: Actual365
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
