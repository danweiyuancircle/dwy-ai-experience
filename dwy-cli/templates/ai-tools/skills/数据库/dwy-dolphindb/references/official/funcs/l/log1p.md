---
source_url: https://docs.dolphindb.cn/zh/funcs/l/log1p.html
fetched_at: 2026-05-19T09:30:21Z
category: funcs
title: log1p
sha1: 80bb6ca7108de23e10c2309fd36eae7edd52be64
---

# log1p

## 语法

`log1p(X)`

## 详情

返回 log(1+X) 的结果。

注：

DolphinDB `log1p` 与 [numpy.log1p](https://numpy.org/doc/stable/reference/generated/numpy.log1p.html) 的核心功能相同，区别在于 DolphinDB
`log1p` 只接受一个参数 *X*，而 `numpy.log1p`
支持更多参数，如 *out*、*where*。

## 参数

**X** 可以是标量、向量、数据对、矩阵或表。

## 返回值

返回数值类型的结果，形式与 *X* 一致。

## 例子

```dolphindb
log1p(2);
// output
1.098612

log1p(2 4 6);
// output
[1.098612,1.609438,1.94591]

log1p(1..4$2:2);
```

| #0 | #1 |
| --- | --- |
| 0.693147 | 1.386294 |
| 1.098612 | 1.609438 |
