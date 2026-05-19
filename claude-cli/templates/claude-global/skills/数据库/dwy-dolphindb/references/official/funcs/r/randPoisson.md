---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randPoisson.html
fetched_at: 2026-05-19T09:35:07Z
category: funcs
title: randPoisson
sha1: 4554c8fbceb7ff04bc361fb8221422b810821891
---

# randPoisson

## 语法

`randPoisson(mean, count)`

## 详情

生成指定个数的泊松分布随机数。

## 参数

**mean** 是泊松分布的均值。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randPoisson(2.31, 2);
// output
[7, 2]
```
