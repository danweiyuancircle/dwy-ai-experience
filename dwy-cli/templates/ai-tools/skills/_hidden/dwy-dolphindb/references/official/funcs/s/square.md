---
source_url: https://docs.dolphindb.cn/zh/funcs/s/square.html
fetched_at: 2026-05-19T09:39:56Z
category: funcs
title: square
sha1: cfbe22950183ee63ee924c3dc8827eac3ac619ea
---

# square

## 语法

`square(X)`

## 详情

返回 *X* 的平方。返回结果的数据类型为 DOUBLE 类型。

## 参数

**X** 可以是标量、数据对、向量或矩阵。

## 返回值

DOUBLE 类型的标量、数据对、向量或矩阵。

## 例子

```dolphindb
square(3);
// output
9

square(2 4 NULL 6);
// output
[4,16,,36]

square(1..4$2:2);
```

| #0 | #1 |
| --- | --- |
| 1 | 9 |
| 4 | 16 |
