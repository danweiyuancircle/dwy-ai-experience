---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mcovarpTopN.html
fetched_at: 2026-05-19T09:31:23Z
category: funcs
title: mcovarpTopN
sha1: ecb409ab04a0f53d8506cba255edcc4b8cad0045
---

# mcovarpTopN

首发版本：3.00.5

## 语法

`mcovarpTopN(X, Y, S, window, top, [ascending=true],
[tiesMethod='oldest'])`

参数说明和窗口计算规则请参考：[mTopN](../themes/TopN.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，根据 *ascending* 指定的排序方式将 *X* 和 *Y* 按照 *S*
进行稳定排序后，取前 *top* 个元素，然后计算 *Y* 和 *X* 的总体协方差。

## 返回值

计算结果为 DOUBLE 类型，形式同输入参数。

## 例子

以 IBM 股票为例，构造连续 6 个交易日的指数收益率、个股收益率和成交量数据：

```dolphindb
symbol = take(`IBM, 6)
tradeDate = 2024.01.02 2024.01.03 2024.01.04 2024.01.05 2024.01.08 2024.01.09
indexRet = [0.6, 1.1, -0.2, 0.9, 1.3, 0.4]
stockRet = [0.9, 1.7, -0.1, 1.4, 1.9, 0.8]
tradeVolume = [520, 860, 610, 940, 650, 880]

stockDaily = table(symbol, tradeDate, indexRet, stockRet, tradeVolume)
stockDaily;
```

输出结果：

| symbol | tradeDate | indexRet | stockRet | tradeVolume |
| --- | --- | --- | --- | --- |
| IBM | 2024.01.02 | 0.6 | 0.9 | 520 |
| IBM | 2024.01.03 | 1.1 | 1.7 | 860 |
| IBM | 2024.01.04 | -0.2 | -0.1 | 610 |
| IBM | 2024.01.05 | 0.9 | 1.4 | 940 |
| IBM | 2024.01.08 | 1.3 | 1.9 | 650 |
| IBM | 2024.01.09 | 0.4 | 0.8 | 880 |

在最近 4 个交易日内，选取成交量最高的前 2 个交易日，计算个股收益率（stockRet ）和指数收益率（indexRet）的总体协方差：

```dolphindb
mcovarTopN(X=indexRet, Y=stockRet, S=tradeVolume, window=4, top=2, ascending=false)
// 输出: [ , 0.2, 1.17, 0.03, 0.03, 0.15]
```

- tradeVolume 用于筛选成交最活跃的交易日；
- 对 2024.01.09 的数据而言，最近 4 日窗口中成交量最高的两个交易日对应样本为 (0.9, 1.4) 和 (0.4,
  0.8)，它们的总体协方差为 0.075。

相关函数：[covarp](../c/covarp.html)
