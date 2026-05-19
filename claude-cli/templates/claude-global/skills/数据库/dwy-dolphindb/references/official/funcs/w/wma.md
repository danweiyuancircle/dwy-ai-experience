---
source_url: https://docs.dolphindb.cn/zh/funcs/w/wma.html
fetched_at: 2026-05-19T09:44:05Z
category: funcs
title: wma
sha1: fed7659b0415219de9e93f5378d020d83f2418b6
---

# wma

## 语法

`wma(X, window)`

TA-lib 系列函数参数说明和窗口计算规则请参考：[TAlib](../themes/TAlib.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，计算 *X* 的加权移动平均（Weighted Moving
Average）。

其计算公式为：

  
![wma](../../images/wma.png)

## 返回值

返回数值类型的结果，形式与 *X* 一致。

## 例子

```dolphindb
x=12.1 12.2 12.6 12.8 11.9 11.6 11.2
wma(x,3);
// output
[,,12.383333333333332,12.633333333333334,12.316666666666668,11.9,11.450000000000001]

x=matrix(12.1 12.2 12.6 12.8 11.9 11.6 11.2, 14 15 18 19 21 12 10)
wma(x,3);
```

| col1 | col2 |
| --- | --- |
|  |  |
|  |  |
| 12.3833 | 16.3333 |
| 12.6333 | 18 |
| 12.3167 | 19.8333 |
| 11.9 | 16.1667 |
| 11.45 | 12.5 |

相关函数：[sma](../s/sma.html), [trima](../t/trima.html)
