---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randNormal.html
fetched_at: 2026-05-19T09:35:03Z
category: funcs
title: randNormal
sha1: c0dd470e39c939b97646587085306b660fa7da29
---

# randNormal

## 语法

`randNormal(mean, stdev, count)`

## 详情

生成指定个数的正态分布随机数。

## 参数

**mean** 是正态分布的均值。

**stdev** 是正态分布的标准差。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randNormal(2.31, 0.671, 2);
// output
[2.805524, 2.148019]
```
