---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentfloatingdaycountconvention.html
fetched_at: 2026-05-19T09:24:14Z
category: funcs
title: getInstrumentFloatingDayCountConvention
sha1: 6873e0100f8a186ec150ae8ba01d5f06a279725c
---

# getInstrumentFloatingDayCountConvention

首发版本：3.00.4.1

## 语法

`getInstrumentFloatingDayCountConvention(instrument)`

## 详情

根据输入的金融工具，获取该工具的浮动端日期计数惯例。

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
getInstrumentFloatingDayCountConvention(instrument)

// output: Actual360
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
