---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mbetaTopN.html
fetched_at: 2026-05-19T09:31:16Z
category: funcs
title: mbetaTopN
sha1: 85792547de7ea2aa1519eb4e107b16ee46f9cdd1
---

# mbetaTopN

## 语法

`mbetaTopN(X, Y, S, window, top, [ascending=true],
[tiesMethod='oldest'])`

参数说明和窗口计算规则请参考：[mTopN](../themes/TopN.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，根据 *ascending* 指定的排序方式将 *X* 和 *Y* 按照 *S*
进行稳定排序后，取前 *top* 个元素，然后计算 *Y* 在 *X* 上的回归系数的最小二乘估计。

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

在最近 4 个交易日内，选取成交量最高的前 2 个交易日，用最小二乘法估计指数收益率（indexRet）对个股收益率（stockRet）的回归系数：

```dolphindb
mbetaTopN(X=stockRet, Y=indexRet, S=tradeVolume, window=4, top=2, ascending=false)
// 输出: [ , 1.6, 1.3846, 1.5, 1.5, 1.2]
```

- stockRet 是回归自变量，indexRet 是回归因变量；
- tradeVolume 用于筛选成交最活跃的交易日；
- 对 2024.01.09 的数据而言，最近 4 日窗口中成交量最高的两个交易日对应样本为 (0.9, 1.4) 和 (0.4, 0.8)；
- 基于这两个样本，用最小二乘法估计 indexRet 对 stockRet 的回归系数，结果为 1.2。

相关函数：[mbeta](mbeta.html)
