---
source_url: https://docs.dolphindb.cn/zh/funcs/k/kama.html
fetched_at: 2026-05-19T09:29:09Z
category: funcs
title: kama
sha1: a8a54cd52ebee26a2baadd181261bd474b7972ad
---

# kama

## 语法

`kama(X, window)`

TA-lib 系列函数参数说明和窗口计算规则请参考：[TA-lib 系列](../themes/TAlib.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，计算 *X* 的考夫曼自适应移动平均值（Kaufman Adaptive
Moving Average）。

## 返回值

DOUBLE 类型，数据形式同 *X*。

## 例子

```dolphindb
x=[51.65, 81.18, 43.37, 11.26, 82.79, 13.4, 81.87, 63.53, 21.28, 94.23]
kama(x, 5);
// output
[,,,,,81.006144,81.009907,80.793626,80.344572,80.456788]

t=table(take(`A`B,10) as sym, rand(100.0,10) as close)
select sym, kama(close, 3) as kama from t context by sym;
```

输出返回：

| sym | kama |
| --- | --- |
| A |  |
| A |  |
| A |  |
| A | 66.342572 |
| A | 62.500023 |
| B |  |
| B |  |
| B |  |
| B | 17.376469 |
| B | 42.27882 |
