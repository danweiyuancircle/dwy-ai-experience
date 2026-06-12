---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getinstrumentfrequency.html
fetched_at: 2026-05-19T09:24:16Z
category: funcs
title: getInstrumentFrequency
sha1: 37d001c52c6f1f7cbb96eeec03237633adb33631
---

# getInstrumentFrequency

首发版本：3.00.4.1

## 语法

`getInstrumentFrequency(instrument)`

## 详情

根据输入的金融工具，获取该工具的付息频率（Coupon Frequency）。

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
getInstrumentFrequency(ins)
// output: Semiannual
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
