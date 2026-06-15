---
source_url: https://docs.dolphindb.cn/zh/funcs/t/tril.html
fetched_at: 2026-05-19T09:42:52Z
category: funcs
title: tril
sha1: 19d83540b4e7df549a48b97f43c84de58f461ae5
---

# tril

## 语法

`tril(X, [k=0])`

## 详情

- 若未指定 *k*： 返回矩阵 *X* 的下三角部分，其余元素设为0。
- 若指定 *k*： 返回矩阵 *X* 的第 *k*
  条对角线上以及该对角线下方的元素，其余元素设为0。矩阵的主对角线为其第0条对角线。

## 参数

**X** 是一个矩阵。

**k** 是一个整数。

## 返回值

返回一个矩阵，其数据类型同 *X*。

## 例子

```dolphindb
m=matrix(1 2 3, 4 5 6, 7 8 9);
m;
```

| col1 | col2 | col3 |
| --- | --- | --- |
| 1 | 4 | 7 |
| 2 | 5 | 8 |
| 3 | 6 | 9 |

```dolphindb
tril(m);
```

| col1 | col2 | col3 |
| --- | --- | --- |
| 1 | 0 | 0 |
| 2 | 5 | 0 |
| 3 | 6 | 9 |

```dolphindb
tril(m,1);
```

| col1 | col2 | col3 |
| --- | --- | --- |
| 1 | 4 | 0 |
| 2 | 5 | 8 |
| 3 | 6 | 9 |

```dolphindb
tril(m,-1);
```

| col1 | col2 | col3 |
| --- | --- | --- |
| 0 | 0 | 0 |
| 2 | 0 | 0 |
| 3 | 6 | 0 |

相关函数：[triu](triu.html)
