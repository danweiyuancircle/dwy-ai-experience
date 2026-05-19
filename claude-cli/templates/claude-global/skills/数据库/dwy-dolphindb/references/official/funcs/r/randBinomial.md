---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randBinomial.html
fetched_at: 2026-05-19T09:34:54Z
category: funcs
title: randBinomial
sha1: 6e84233ce779800b9da5340aad86ebd2a9719fd3
---

# randBinomial

## 语法

`randBinomial(trials, p, count)`

## 详情

生成指定个数的二项分布随机数。

## 参数

**trials** 是正整数。

**p** 是0到1之间的浮点数。

**trials** 和 **p** 是形状参数。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randBinomial(2, 0.627, 2);
// output
[1, 1]
```
