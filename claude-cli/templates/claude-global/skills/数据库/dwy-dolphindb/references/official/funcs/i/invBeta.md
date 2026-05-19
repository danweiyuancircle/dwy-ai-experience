---
source_url: https://docs.dolphindb.cn/zh/funcs/i/invBeta.html
fetched_at: 2026-05-19T09:27:55Z
category: funcs
title: invBeta
sha1: 593dc1391e9ec1f97fc405c0304fbc72ee50cc8e
---

# invBeta

## 语法

`invBeta(alpha, beta, X)`

## 详情

返回 Beta 分布的累计密度函数的逆函数值。

## 参数

形状参数 **alpha** 和 **beta** 都是正数。

**X** 是 0 到 1 之间的浮点型标量或向量。

## 返回值

DOUBLE 类型标量或向量。

## 例子

```dolphindb
invBeta(2.31, 0.627, [0.001, 0.5, 0.999]);
// output
[0.068102, 0.852866, 0.999994]

invBeta(2.31, 0.627, [0.1, 0.3, 0.5, 0.7, 0.9]);
// output
[0.471316, 0.717156, 0.852866, 0.939378, 0.989912]]
```
