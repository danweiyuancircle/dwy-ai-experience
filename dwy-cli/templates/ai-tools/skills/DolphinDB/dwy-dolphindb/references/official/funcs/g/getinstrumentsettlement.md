---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentsettlement.html
fetched_at: 2026-05-19T09:24:34Z
category: funcs
title: getInstrumentSettlement
sha1: b6ca57cb9441c76aa550dc2186277a9867477cba
---

# getInstrumentSettlement

首发版本：3.00.4.1

## 语法

`getInstrumentSettlement(instrument)`

## 详情

根据输入的金融工具，获取该工具的结算日（Settlement Date）。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DATE 类型标量或向量。

## 例子

```dolphindb
bond = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "ZeroCouponBond",
    "instrumentId": "0001",
    "start": 1996.03.01,
    "maturity": 2032.05.15,
    "dayCountConvention": "ActualActualISDA",
    "coupon": 0.0276,
    "issuePrice": 100.0,
    "frequency": "Semiannual",
    "subType":"TREASURY_BOND",
    "creditRating":"B",
    "settlement": 2022.05.15 
}
ins = parseInstrument(bond)
getInstrumentSettlement(ins)
// output: 2022.05.15
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
