---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentrate.html
fetched_at: 2026-05-19T09:24:33Z
category: funcs
title: getInstrumentRate
sha1: f2edff137f46bf9badf1ad7e899eeaf23df74d6a
---

# getInstrumentRate

首发版本：3.00.4.1

## 语法

`getInstrumentRate(instrument)`

## 详情

根据输入的金融工具，获取该工具的存款利率。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
deposit =  {
    "productType": "Cash",
    "assetType": "Deposit",
    "start": 2025.05.15,
    "maturity": 2025.08.15,
    "rate": 0.02,
    "dayCountConvention": "Actual360",
    "notionalCurrency": "CNY",
    "notionalAmount": 1E6,
    "payReceive": "Receive"
}
instrument = parseInstrument(deposit)
getInstrumentRate(instrument)

// output: 0.02
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
