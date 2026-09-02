---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getInstrumentCoupon.html
fetched_at: 2026-05-19T09:23:58Z
category: funcs
title: getInstrumentCoupon
sha1: 2e7faa45ee3c0adbc84b59bc45adf037ee9e100d
---

# getInstrumentCoupon

首发版本：3.00.4.1

## 语法

`getInstrumentCoupon(instrument)`

## 详情

根据输入的金融工具，获取该工具的票面利率（Coupon Rate）。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

## 返回值

DOUBLE 类型标量或向量。

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
getInstrumentCoupon(ins)
// output: 0.0276
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentField](getInstrumentField.html)、[getInstrumentKeys](getInstrumentKeys.html)
