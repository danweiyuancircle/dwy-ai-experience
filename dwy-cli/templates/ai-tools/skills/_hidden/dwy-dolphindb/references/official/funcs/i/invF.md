---
source_url: https://docs.dolphindb.cn/zh/funcs/i/invF.html
fetched_at: 2026-05-19T09:28:01Z
category: funcs
title: invF
sha1: 4bdca5de2b14e2ef262d4591ec3ad2e1193c82ed
---

# invF

## 语法

`invF(numeratorDF, denominatorDF, X)`

## 详情

返回F分布的累计密度函数的逆函数值。

## 参数

**numeratorDF** 和 **denominatorDF** 都是正数，表示F分布的自由度。

**X** 是0到1之间的浮点型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
invF(2.31, 0.627, [0.001, 0.5, 0.7]);
// output: [0.002024, 2.69427, 14.992595]

invF(2.31,0.627, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output: [0.146649, 0.718555, 2.69427, 14.992595, 508.444221]
```
