---
source_url: https://docs.dolphindb.cn/zh/funcs/m/ma.html
fetched_at: 2026-05-19T09:30:41Z
category: funcs
title: ma
sha1: 0c2de4ab77d85670e8c48042b747b362589a33ba
---

# ma

## 语法

`ma(X, window, maType)`

TA-lib 系列函数其他通用参数说明和窗口计算规则请参考：[TA-lib 系列](../themes/TAlib.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，计算 *X* 的移动平均，计算公式由 *maType* 决定。

## 参数

**maType** 计算平均线的方法。是一个0-8范围内的整数。各个整数分别表示：0= [sma](../s/sma.html) , 1= [ema](../e/ema.html) , 2=
[wma](../w/wma.html) , 3= [dema](../d/dema.html) , 4= [tema](../t/tema.html) , 5= [trima](../t/trima.html) , 6= [kama](../k/kama.html)
, 8= [t3](../t/t3.html)。注意：暂不支持 7 (mama)。

## 返回值

DOUBLE 类型向量。
