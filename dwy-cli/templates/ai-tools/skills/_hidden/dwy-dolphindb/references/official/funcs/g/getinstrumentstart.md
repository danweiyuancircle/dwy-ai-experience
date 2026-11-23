---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentstart.html
fetched_at: 2026-05-19T09:24:36Z
category: funcs
title: getInstrumentStart
sha1: 3475dc64c4d5188f3ec75ef7d0cae1f62f3d8446
---

# getInstrumentStart

首发版本：3.00.4.1

## 语法

`getInstrumentStart(instrument)`

## 详情

根据输入的金融工具，获取该工具的起始日（Start Date）。

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
getInstrumentStart(ins)
// output: 1996.03.01
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
