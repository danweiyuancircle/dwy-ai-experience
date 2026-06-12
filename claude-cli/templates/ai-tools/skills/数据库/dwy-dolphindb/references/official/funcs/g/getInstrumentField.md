---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getInstrumentField.html
fetched_at: 2026-05-19T09:24:11Z
category: funcs
title: getInstrumentField
sha1: 8965374e2d0b6ded32223d95b407e8da287568c5
---

# getInstrumentField

首发版本：3.00.4.1

## 语法

`getInstrumentField(instrument, key,
[default])`

## 详情

从金融工具中提取指定字段（*key*）对应的值：

- 未设置 *default* 时，若字段存在有效值，则返回该值，否则返回空值；
- 设置 *default* 时，若字段存在有效值，则将其类型转为 *default* 的类型返回，否则返回
  *default*。

## 参数

**instrument** INSTRUMENT 类型标量或向量，表示金融工具。

**key** STRING 类型标量，表示金融工具的字段，需与 *instrument* 中定义的字段名一致。

**default** 一个标量，表示 *key* 的默认值。目前支持如下类型：LOGICAL, INTEGRAL（COMPRESSED 除外）,
TEMPORAL（DATEHOUR 除外）, FLOATING, LITERAL, DECIMAL。

## 返回值

- 当 *instrument* 是标量时，返回一个标量。
- 当 *instrument* 是向量时，返回一个与 *instrument* 等长的向量。

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
getInstrumentField(ins, "productType")
// output: Cash
```

**相关函数：**[parseInstrument](../p/parseInstrument.html)、[getInstrumentKeys](getInstrumentKeys.html)
