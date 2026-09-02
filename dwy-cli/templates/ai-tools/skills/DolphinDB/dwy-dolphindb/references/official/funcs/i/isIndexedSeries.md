---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isIndexedSeries.html
fetched_at: 2026-05-19T09:28:29Z
category: funcs
title: isIndexedSeries
sha1: feaa44426680786729247c9523528f33434a1aae
---

# isIndexedSeries

## 语法

`isIndexedSeries(X)`

## 详情

判断 *X* 是否为有索引的序列。

## 参数

**X** 是一个单列矩阵。

## 返回值

布尔标量。

## 例子

```dolphindb
s=matrix(1..10).rename!(2020.01.01..2020.01.10, );

isIndexedSeries(s);
// output: false

s.setIndexedSeries!()
isIndexedSeries(s);
// output: true
```
