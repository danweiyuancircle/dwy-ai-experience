---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentcurrency.html
fetched_at: 2026-05-19T09:24:01Z
category: funcs
title: getInstrumentCurrency
sha1: 3a6da9208348a28e3029b62a1edc6b548d91debc
---

# getInstrumentCurrency

首发版本：3.00.4.1

## 语法

`getInstrumentCurrency(instrument)`

## 详情

根据输入的金融工具，获取该工具的货币类型。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

STRING 类型标量或向量。

## 例子

```dolphindb
bond = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "FixedRateBond",
    "nominal": 100,
    "instrumentId": "0001",
    "start": 2022.05.15,
    "maturity": 2032.05.15,
    "dayCountConvention": "ActualActualISDA",
    "coupon": 0.0276,
    "issuePrice": 100.0,
    "frequency": "Semiannual",
    "currency": "USD"
}
ins = parseInstrument(bond)
getInstrumentCurrency(ins)
// output: USD
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
