---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randLogistic.html
fetched_at: 2026-05-19T09:35:01Z
category: funcs
title: randLogistic
sha1: e981d16144c6a74a3e8a633ee63c4a263b4de287
---

# randLogistic

## 语法

`randLogistic(mean, s, count)`

## 详情

生成指定个数的 Logistic 分布随机数。

## 参数

**mean** Logistic 分布的均值。

**s** 是Logistic 分布的尺度参数。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randLogistic(2.31, 0.671, 2);
// output
[2.465462, 2.577171]
```
