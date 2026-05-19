---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentfixedrate.html
fetched_at: 2026-05-19T09:24:13Z
category: funcs
title: getInstrumentFixedRate
sha1: 250c5b5e5c06331d954d3cc14e87517dd4adacb6
---

# getInstrumentFixedRate

首发版本：3.00.4.1

## 语法

`getInstrumentFixedRate(instrument)`

## 详情

根据输入的金融工具，获取该工具的固定端利率。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DOUBLE 类型标量或向量。

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
getInstrumentFixedRate(instrument)

// output: 0.02
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
