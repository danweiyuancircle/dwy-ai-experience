---
source_url: https://docs.dolphindb.cn/zh/funcs/l/log.html
fetched_at: 2026-05-19T09:30:19Z
category: funcs
title: log
sha1: 13973497000ec8c02a68fba2d7a3cd3955e69e97
---

# log

## 语法

`log(X, [Y])`

## 详情

若未指定 *Y*，返回 *X* 的自然对数（以常数 e 为底）；若指定了 *Y*，则返回以 *Y* 为底的 *X*
的对数。

## 参数

**X** 可以是标量、向量、数据对、矩阵或表。

**Y** 可选参数。是一个正数，表示对数的底。

## 返回值

返回数值类型的结果，形式与 *X* 一致。

## 例子

```dolphindb
log(2.718283);
```

输出返回：1

```dolphindb
log(0 1 2 3);
```

输出返回：[,0,0.693147,1.098612]

```dolphindb
log(100, 10)
```

输出返回：2
