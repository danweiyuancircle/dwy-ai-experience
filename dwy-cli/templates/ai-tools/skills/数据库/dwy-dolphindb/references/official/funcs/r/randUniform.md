---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randUniform.html
fetched_at: 2026-05-19T09:35:09Z
category: funcs
title: randUniform
sha1: c42871842cb4a6bde7b3c099024ab39241fa7c22
---

# randUniform

## 语法

`randUniform(lower, upper, count)`

## 详情

生成指定个数的均匀分布随机数。

## 参数

**lower** 和 **upper** 是数值型标量，表示连续均匀分布的下限和上限。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randUniform(0.61, 2.31, 2);

// output
[2.064851, 2.263172]
```
