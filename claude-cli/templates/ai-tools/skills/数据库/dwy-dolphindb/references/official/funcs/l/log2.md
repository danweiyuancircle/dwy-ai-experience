---
source_url: https://docs.dolphindb.cn/zh/funcs/l/log2.html
fetched_at: 2026-05-19T09:30:22Z
category: funcs
title: log2
sha1: e49c711fc8d2ed78410470af9339ff2369f10bfc
---

# log2

## 语法

`log2(X)`

## 详情

求以2为底，*X* 的对数。

注：

DolphinDB `log2` 与 [numpy.log2](https://numpy.org/doc/stable/reference/generated/numpy.log2.html) 的核心功能相同，区别在于 DolphinDB
`log2` 只接受一个参数 *X*，而 `numpy.log2`
支持更多参数，如 *out*、*where*。

## 参数

**X** 可以是标量、向量、数据对、矩阵或表。

## 返回值

返回数值类型的结果，形式和 *X* 一致。

## 例子

```dolphindb
log2(4);
// output
2

log2(0 2 4 8 NULL);
// output
[,1,2,3,]

log2(1..4$2:2);
```

| #0 | #1 |
| --- | --- |
| 0 | 1.584963 |
| 1 | 2 |
