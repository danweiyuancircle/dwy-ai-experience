---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mwsumTopN.html
fetched_at: 2026-05-19T09:33:03Z
category: funcs
title: mwsumTopN
sha1: 066e4f5e01531fd3be33bed5f89476eb3bb0dca8
---

# mwsumTopN

## 语法

`mwsumTopN(X, Y, S, window, top, [ascending=true],
[tiesMethod='oldest'])`

参数说明和窗口计算规则请参考：[mTopN](../themes/TopN.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，根据 *ascending* 指定的排序方式将 *X* 和 *Y* 按照 *S*
进行稳定排序后，取前 *top* 个元素，然后计算 *Y* 和 *X* 的内积。

## 返回值

- 输入为向量时，返回一个与输入等长的 DOUBLE 类型向量。
- 输入为矩阵时，返回一个与输入矩阵同维度的矩阵，每列分别计算。
- 输入为表时，返回一个与输入表结构相同的表。
- 输入为元组时，返回对应的元组结构。

## 例子

以 IBM 股票为例，构造连续 6 个交易日的股票成交价格、成交量和换手率数据：

```dolphindb
symbol = take(`IBM, 6)
tradeDate = 2024.01.02 2024.01.03 2024.01.04 2024.01.05 2024.01.08 2024.01.09
tradePrice = [182.5, 183.8, 181.2, 184.6, 183.1, 185.0]
tradeVolume = [520, 860, 610, 940, 650, 880]
turnoverRate = [1.8, 2.6, 1.9, 3.1, 2.1, 2.8]

stockDaily = table(symbol, tradeDate, tradePrice, tradeVolume, turnoverRate)
stockDaily;
```

输出结果：

| symbol | tradeDate | tradePrice | tradeVolume | turnoverRate |
| --- | --- | --- | --- | --- |
| IBM | 2024.01.02 | 182.5 | 520 | 1.8 |
| IBM | 2024.01.03 | 183.8 | 860 | 2.6 |
| IBM | 2024.01.04 | 181.2 | 610 | 1.9 |
| IBM | 2024.01.05 | 184.6 | 940 | 3.1 |
| IBM | 2024.01.08 | 183.1 | 650 | 2.1 |
| IBM | 2024.01.09 | 185 | 880 | 2.8 |

在最近 4 个交易日内，选取换手率最高的前 2 个交易日，计算成交价格（tradePrice）与成交量（tradeVolume）的内积：

```dolphindb
mwsumTopN(X=tradePrice, Y=tradeVolume, S=turnoverRate, window=4, top=2, ascending=false)
// 输出: [94,900, 252,968, 268,600, 331,592, 331,592, 336,324]
```

- turnoverRate 用于筛选换手率最高的交易日；
- 对 2024.01.09 的数据而言，最近 4 日窗口中换手率最高的两个交易日对应样本为(184.6, 940) 和 (185.0, 880)，其内积为
  184.6\*940 + 185.0\*880 = 336,324。

相关函数：[mwsum](mwsum.html)
