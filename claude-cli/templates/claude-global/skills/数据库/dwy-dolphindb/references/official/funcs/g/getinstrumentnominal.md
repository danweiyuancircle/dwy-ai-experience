---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentnominal.html
fetched_at: 2026-05-19T09:24:26Z
category: funcs
title: getInstrumentNominal
sha1: 2c4df93abaf0c0d4785ee1100958750437ebe773
---

# getInstrumentNominal

首发版本：3.00.4.1

## 语法

`getInstrumentNominal(instrument)`

## 详情

根据输入的金融工具，获取该工具的名义金额（nominal）。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
deposit =  {
    "productType": "Cash",
    "assetType": "Deposit",
    "nominal":100,
    "start": 2025.05.15,
    "maturity": 2025.08.15,
    "rate": 0.02,
    "dayCountConvention": "Actual360",
    "notionalCurrency": "CNY",
    "notionalAmount": 1E6,
    "payReceive": "Receive"
}
ins = parseInstrument(deposit)
getInstrumentNominal(ins)

// output: 100
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
