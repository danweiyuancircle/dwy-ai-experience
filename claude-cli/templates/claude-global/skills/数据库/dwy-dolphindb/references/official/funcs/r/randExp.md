---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randExp.html
fetched_at: 2026-05-19T09:34:58Z
category: funcs
title: randExp
sha1: 2472a53661d20ced7e378e84e7d8344ba327d99e
---

# randExp

## 语法

`randExp(mean, count)`

## 详情

生成指定个数的指数分布随机数。

## 参数

**mean** 是指数分布的均值。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randExp(2.31, 2);
// output
[0.732791, 0.732791]
```
