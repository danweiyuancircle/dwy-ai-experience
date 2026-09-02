---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randGamma.html
fetched_at: 2026-05-19T09:35:00Z
category: funcs
title: randGamma
sha1: 2a015befb7bdddc108d21a23c1bfc98be70a8a7b
---

# randGamma

## 语法

`randGamma(shape, scale, count)`

## 详情

生成指定个数的 Gamma 分布随机数。

## 参数

形状参数 **shape** 是正数。

形状参数 **scale** 是正数。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randGamma(2.31, 0.671, 2);
// output
[0.784424, 0.716934]
```
