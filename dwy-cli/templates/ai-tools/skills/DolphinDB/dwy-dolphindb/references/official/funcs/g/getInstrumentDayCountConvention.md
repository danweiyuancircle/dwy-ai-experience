---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getInstrumentDayCountConvention.html
fetched_at: 2026-05-19T09:24:03Z
category: funcs
title: getInstrumentDayCountConvention
sha1: 7f37b2d9a7f5124a6043368d780af767f6bb8826
---

# getInstrumentDayCountConvention

首发版本：3.00.4.1

## 语法

`getInstrumentDayCountConvention(instrument)`

## 详情

根据输入的金融工具，获取该工具的计息日规则（Day Count Convention）。

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
    "frequency": "Semiannual"
}
ins = parseInstrument(bond)
getInstrumentDayCountConvention(ins)
// output: ActualActualISDA
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
