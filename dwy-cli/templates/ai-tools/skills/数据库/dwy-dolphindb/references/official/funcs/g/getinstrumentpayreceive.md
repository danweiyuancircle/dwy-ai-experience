---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentpayreceive.html
fetched_at: 2026-05-19T09:24:31Z
category: funcs
title: getInstrumentPayReceive
sha1: ad1c36e655b110c7f749c6e22b53f90ab2673ff1
---

# getInstrumentPayReceive

首发版本：3.00.4.1

## 语法

`getInstrumentPayReceive(instrument)`

## 详情

根据输入的金融工具，获取该工具的收付标识。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

STRING 类型标量或向量。

## 例子

```dolphindb
swap = {
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
ins = parseInstrument(swap)
getInstrumentPayReceive(ins)
// output: Pay
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
