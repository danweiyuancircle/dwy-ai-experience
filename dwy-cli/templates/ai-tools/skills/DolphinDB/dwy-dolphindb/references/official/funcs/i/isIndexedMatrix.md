---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isIndexedMatrix.html
fetched_at: 2026-05-19T09:28:28Z
category: funcs
title: isIndexedMatrix
sha1: 810adc387735374cbd2f79b79de48b3d979bc229
---

# isIndexedMatrix

## 语法

`isIndexedMatrix(X)`

## 详情

判断 *X* 是否为有索引的矩阵。

## 参数

**X** 是一个矩阵。

## 返回值

布尔标量。

## 例子

```dolphindb
m=matrix(1..10, 11..20)
m.rename!(2020.01.01..2020.01.10, `A`B);

isIndexedMatrix(m);
// output: false

m.setIndexedMatrix!()
isIndexedMatrix(m);
// output: true
```
