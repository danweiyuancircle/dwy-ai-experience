---
source_url: https://docs.dolphindb.cn/zh/funcs/l/log10.html
fetched_at: 2026-05-19T09:30:23Z
category: funcs
title: log10
sha1: 561dcb20b6c5c2ac21db8003f8c312dba1995a13
---

# log10

## 语法

`log10(X)`

## 详情

求以10为底，*X* 的对数。

## 参数

**X** 可以是标量、向量、数据对、矩阵或表。

## 返回值

返回数值类型的结果，形式和 *X* 一致。

## 例子

```dolphindb
log10(100);
// output
2

log10(0 10 20 30 NULL);
// output
[,1,1.30103,1.477121,]

log10(1..4$2:2);
```

| #0 | #1 |
| --- | --- |
| 0 | 0.477121 |
| 0.30103 | 0.60206 |
