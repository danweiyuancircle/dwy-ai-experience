---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mpercentiletopn.html
fetched_at: 2026-05-19T09:32:32Z
category: funcs
title: mpercentileTopN
sha1: b29b2cf25559f9612038f50d1ee201f18c22dbee
---

# mpercentileTopN

## 语法

`mpercentileTopN(X, S, percent, window, top, [interpolation], [ascending],
[tiesMethod='oldest'])`

参数说明和窗口计算规则请参考：[mTopN](../themes/TopN.html)

## 详情

- 若 *X* 是向量，在长度为 *window* 的滑动窗口内，根据 *ascending* 指定的排序方式将
  *X* 在窗口内的元素按照 *S* 进行稳定排序，取其前*top* 个元素计算对应的 *percent*百分位数。
- 若 *X* 是矩阵或表，在每列内进行上述计算，返回同样数据类型和数据维度的结果。

## 参数

**percent** 是 0 到 100之间的数，表示计算的百分位数。

**interpolation** 是一个字符串，表示当选中的分位点位于在 *X* 的第 i 和第 i+1
个元素之间时，采用的插值方法。它具有以下取值，默认值为 'linear'：

- ‘linear’：Xi + ( Xi+1 - Xi ) \* fraction，其中
  fraction 为![](../../images/fraction.png)
- 'lower'：Xi
- 'higher’：Xi+1
- 'nearest'： Xi+1 和 Xi 之中最接近分位点的数据
- 'midpoint'：（Xi+1 + Xi )/2

## 返回值

- 输入为向量时，返回一个与输入等长的 DOUBLE 类型向量。
- 输入为矩阵时，返回一个与输入矩阵同维度的矩阵，每列分别计算。
- 输入为表时，返回一个与输入表结构相同的表。
- 输入为元组时，返回对应的元组结构。

## 例子

以 IBM 股票为例，构造连续 6 个交易日的成交价格和成交量数据：

```dolphindb
symbol = take(`IBM, 6)
tradeDate = 2024.01.02 2024.01.03 2024.01.04 2024.01.05 2024.01.08 2024.01.09
tradePrice = [182.5, 183.8, 181.2, 184.6, 183.1, 185.0]
tradeVolume = [520, 860, 610, 940, 650, 880]

stockDaily = table(symbol, tradeDate, tradePrice, tradeVolume)
stockDaily;
```

输出结果：

| symbol | tradeDate | tradePrice | tradeVolume |
| --- | --- | --- | --- |
| IBM | 2024.01.02 | 182.5 | 520 |
| IBM | 2024.01.03 | 183.8 | 860 |
| IBM | 2024.01.04 | 181.2 | 610 |
| IBM | 2024.01.05 | 184.6 | 940 |
| IBM | 2024.01.08 | 183.1 | 650 |
| IBM | 2024.01.09 | 185 | 880 |

例 1：在最近 4 个交易日中，选取成交量最高的前 2 个交易日，分别计算其成交价格的 50 分位数：

```dolphindb
mpercentileTopN(X=tradePrice, S=tradeVolume, percent=50, window=4, top=2, ascending=false)
// 输出: [182.5, 183.15, 182.5, 184.2, 184.2, 184.8]
```

- 对 2024.01.09 的数据而言，最近 4 日窗口中：

  - tradePrice=[181.2, 184.6, 183.1, 185.0]
  - tradeVolume=[610, 940, 650, 880]
- 因为 *ascending*=false，对成交量执行降序，选取成交量最高的前 2 个交易日，其对应的成交价格为 184.6 和
  185.0；这两个价格的 50 分位数为 184.8。

例 2：设置 *interpolation* 决定分位点位于两个观测值之间的取值方式。

下面仍使用同一组成交价格和成交量数据，在最近 4 个交易日内，选取成交量最低的前 2 个交易日，分别计算其成交价格的 20 分位数：

```dolphindb
mpercentileTopN(X=tradePrice, S=tradeVolume, percent=20, window=4, top=2, interpolation="lower")
// 输出: [182.5, 182.5, 181.2, 181.2, 181.2, 181.2]
​
mpercentileTopN(X=tradePrice, S=tradeVolume, percent=20, window=4, top=2, interpolation="higher")
// 输出: [182.5, 183.8, 182.5, 182.5, 183.1, 183.1]
​
mpercentileTopN(X=tradePrice, S=tradeVolume, percent=20, window=4, top=2, interpolation="nearest")
// 输出: [182.5, 182.5, 181.2, 181.2, 181.2, 181.2]
​
mpercentileTopN(X=tradePrice, S=tradeVolume, percent=20, window=4, top=2, interpolation="midpoint")
// 输出: [182.5, 183.15, 181.85, 181.85, 182.15, 182.15]
​
mpercentileTopN(X=tradePrice, S=tradeVolume, percent=20, window=4, top=2, interpolation="linear")
// 输出: [182.5, 182.76, 181.46, 181.46, 181.58, 181.58]
```

以 2024.01.09 的数据为例，按默认升序选择成交量最低的前 2 个交易日，其对应的成交价格是 181.2 和 183.1：

- *interpolation*="lower"：取较低价格 181.2；
- *interpolation*="higher"：取较高价格 183.1；
- *interpolation*="nearest"：取距离分位点最近的价格 181.2；
- *interpolation*="midpoint"：取两者中点 182.15；
- *interpolation*="linear"：按位置做线性插值，将数据代入 Xi + (
  Xi+1 - Xi ) \* fraction 计算，得到 181.2 + (183.1 -
  181.2) \* 0.2 = 181.58。

例 3：设置 *tiesMethod* 决定边界值并列时如何选样本。

单独构造一组 NVDA 股票的数据：

```dolphindb
symbol = take(`NVDA, 6)
tradeDate = 2024.02.01 2024.02.02 2024.02.05 2024.02.06 2024.02.07 2024.02.08
tradePrice = [431.2, 433.5, 432.1, 434.8, 433.0, 435.2]
tradeVolume = [700, 900, 900, 900, 760, 900]

tieCase = table(symbol, tradeDate, tradePrice, tradeVolume)
tieCase;
```

输出结果：

| symbol | tradeDate | tradePrice | tradeVolume |
| --- | --- | --- | --- |
| NVDA | 2024.02.01 | 431.2 | 700 |
| NVDA | 2024.02.02 | 433.5 | 900 |
| NVDA | 2024.02.05 | 432.1 | 900 |
| NVDA | 2024.02.06 | 434.8 | 900 |
| NVDA | 2024.02.07 | 433.0 | 760 |
| NVDA | 2024.02.08 | 435.2 | 900 |

在最近 5 个交易日内，选取成交量最高的前 2 个交易日，分别计算其成交价格的 50 分位数，并指定不同的 *tiesMethod*：

```dolphindb
mpercentileTopN(X=tradePrice, S=tradeVolume, percent=50, window=5, top=2, ascending=false, tiesMethod="oldest")
// 输出: [431.2, 432.35, 432.8, 432.8, 432.8, 432.8]

mpercentileTopN(X=tradePrice, S=tradeVolume, percent=50, window=5, top=2, ascending=false, tiesMethod="latest")
// 输出: [431.2, 432.35, 432.8, 433.45, 433.45, 435.0]

mpercentileTopN(X=tradePrice, S=tradeVolume, percent=50, window=5, top=2, ascending=false, tiesMethod="all")
// 输出: [431.2, 432.35, 432.8, 433.5, 433.5, 434.15]
```

以 2024.02.08 的数据为例，最近 5 日窗口中的 tradeVolume=[900, 900, 900, 760, 900]，共有 4
个交易日的成交量都并列为最高值 900，但 *top*=2 只要求保留前 2 个名次：

- *tiesMethod*="oldest"：取最早进入窗口的两个成交量最高的交易日，对应价格为 433.5 和 432.1；
- *tiesMethod*="latest"：取最晚进入窗口的两个成交量最高的交易日，对应价格为 434.8 和 435.2；
- *tiesMethod*="all"：保留全部并列的成交量最高的交易日，对应价格为 433.5、432.1、434.8、435.2。
