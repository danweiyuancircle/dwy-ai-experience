---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentsubtype.html
fetched_at: 2026-05-19T09:24:38Z
category: funcs
title: getInstrumentSubType
sha1: acb959136284e46f305e9d7f8e2ab1a11f91008e
---

# getInstrumentSubType

首发版本：3.00.4.1

## 语法

`getInstrumentSubType(instrument)`

## 详情

根据输入的金融工具，获取它的债券子类型。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

STRING 类型标量或向量。

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
getInstrumentSubType(ins)
// output: TREASURY_BOND
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
