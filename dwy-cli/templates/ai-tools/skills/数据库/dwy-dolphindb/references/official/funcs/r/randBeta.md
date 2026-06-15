---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randBeta.html
fetched_at: 2026-05-19T09:34:53Z
category: funcs
title: randBeta
sha1: ccf06672cf79361d79754744556ade8a6af29c44
---

# randBeta

## 语法

`randBeta(alpha, beta, count)`

## 详情

生成指定个数的 Beta 分布随机数。

## 参数

形状参数 **alpha** 和 **beta** 都是正数。

**count** 是正整数，表示生成随机数的个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randBeta(2.31, 0.627, 2);
// output
[0.781246, 0.951372]
```
