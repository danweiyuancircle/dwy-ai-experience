---
source_url: https://docs.dolphindb.cn/zh/funcs/e/ema.html
fetched_at: 2026-05-19T09:20:37Z
category: funcs
title: ema
sha1: 121ac71a654960e80956ecd04f3b95b1fdc2b893
---

# ema

## 语法

`ema(X, window, warmup=false)`

TA-lib 系列函数参数说明和窗口计算规则请参考：[TA-lib 系列](../themes/TAlib.html)

## 详情

在给定长度（以元素个数衡量）的滑动窗口内，计算 *X* 的指数移动平均（Exponential Moving
Average）。

其计算公式如下，其中 EMAk 为第 k 个指数移动平均值，n 为移动窗口长度，Xk
为向量 X 中第 k 个元素。

- *warmup*=false：

  - 前 n-1 个值：直接返回空值（不计算）
  - 第 n 个值（第一个 EMA）：

    EMA(X)
    n
    =

    1
    n

    ∑

    i
    =
    1
    n

    X
    i
  - 从第 n+1 个开始：  
    ![EMA_k](../../images/ema_k.png)

- *warmup*=true:

  ![EMA_ktrue](../../images/ema_ktrue.png)

  其中，向量 X 的定义为：X=[Xk-n, …, Xk-1]

## 参数

**warmup** 布尔值，默认为 false，即计算结果的前 *window*-1 个元素为空值。若为 true，则结果的前
*window*-1 元素将由详情给出的公式计算得出。

## 返回值

返回 DOUBLE 类型，数据形式同 *X*。

## 例子

```dolphindb
x=12.1 12.2 12.6 12.8 11.9 11.6 11.2
ema(x,3);
// output: [,,12.3,12.55,12.225,11.9125,11.55625]

ema(x,3, warmup=true)
// output: [12.1,12.2,12.4667,12.6333,12.2667,11.9333,11.5667]

x=matrix(12.1 12.2 12.6 12.8 11.9 11.6 11.2, 14 15 18 19 21 12 10)
ema(x,3);
```

| #0 | #1 |
| --- | --- |
|  |  |
|  |  |
| 12.30 | 15.666667 |
| 12.55 | 17.333333 |
| 12.225 | 19.166667 |
| 11.9125 | 15.583333 |
| 11.55625 | 12.791667 |

相关函数：[gema](../g/gema.html), [wilder](../w/wilder.html), [dema](../d/dema.html), [tema](../t/tema.html)
