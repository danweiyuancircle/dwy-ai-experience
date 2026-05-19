---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sma.html
fetched_at: 2026-05-19T09:39:32Z
category: funcs
title: sma
sha1: 9955c62336eb0262057321e47111c663f02e021a
---

# sma

## 语法

`sma(X, window)`

TA-lib 系列函数参数说明和窗口计算规则请参考：[TAlib](../themes/TAlib.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，计算 *X* 的简单移动平均（Simple Moving
Average）。

其计算公式为：

  
![](../../images/sma.png)

## 返回值

DOUBLE 类型向量。

## 例子

```dolphindb
x=12.1 12.2 12.6 12.8 11.9 11.6 11.2
sma(x,3);
// output
[,,12.299999999999998,12.533333333333331,12.433333333333331,12.099999999999999,11.566666666666664]

x=matrix(12.1 12.2 12.6 12.8 11.9 11.6 11.2, 14 15 18 19 21 12 10)
sma(x,3);
```

| col1 | col2 |
| --- | --- |
|  |  |
|  |  |
| 12.3 | 15.6667 |
| 12.5333 | 17.3333 |
| 12.4333 | 19.3333 |
| 12.1 | 17.3333 |
| 11.5667 | 14.3333 |

相关函数：[wma](../w/wma.html), [trima](../t/trima.html)
