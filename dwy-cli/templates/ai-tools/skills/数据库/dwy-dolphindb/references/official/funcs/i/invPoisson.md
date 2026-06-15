---
source_url: https://docs.dolphindb.cn/zh/funcs/i/invPoisson.html
fetched_at: 2026-05-19T09:28:05Z
category: funcs
title: invPoisson
sha1: fa6e07a666aa7847d33ffffc114744eacb229fb0
---

# invPoisson

## 语法

`invPoisson(mean, X)`

## 详情

返回泊松分布的累计分布函数的逆函数值。

## 参数

**mean** 是泊松分布的均值。

**X** 是0到1之间的浮点型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
invPoisson(1, [0.91, 0.92, 0.93]);
// output: [2, 3, 3]

invPoisson(3, [0.81, 0.83, 0.95, 0.97, 0.99]);
// output: [4, 5, 6, 7, 8]
```
