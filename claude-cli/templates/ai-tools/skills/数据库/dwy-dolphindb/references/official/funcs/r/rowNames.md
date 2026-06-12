---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rowNames.html
fetched_at: 2026-05-19T09:37:17Z
category: funcs
title: rowNames
sha1: f0850cc89b23d3c55450a36b7e9c598773f33787
---

# rowNames

## 语法

`rowNames(X)`

## 详情

返回矩阵 *X* 的行名。参见相关函数： [columnNames](../c/columnNames.html)

## 参数

**X** 是一个矩阵

## 返回值

返回一个向量。

## 例子

```dolphindb
x=1..6$2:3;
x
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 5 |
| 2 | 4 | 6 |

```dolphindb
x.rename!(1 2, `a`b`c);
```

|  | a | b | c |
| --- | --- | --- | --- |
| 1 | 1 | 3 | 5 |
| 2 | 2 | 4 | 6 |

```dolphindb
rowNames x;
// output
[1,2]
```
