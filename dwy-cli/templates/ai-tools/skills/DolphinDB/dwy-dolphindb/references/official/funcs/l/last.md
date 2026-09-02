---
source_url: https://docs.dolphindb.cn/zh/funcs/l/last.html
fetched_at: 2026-05-19T09:29:26Z
category: funcs
title: last
sha1: 82da68795eb75ace963b299ba95f0f409dd9630a
---

# last

## 语法

`last(X)`

或

`last X`

## 详情

返回向量的最后一个元素，或矩阵、表的最后一行。

注：

若向量的最后一个元素为 NULL，则返回 NULL。若要返回最后一个非 NULL 的元素，请使用 [lastNot](lastNot.html) 函数。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

- 如果 *X* 是一个标量/向量，返回一个标量。
- 如果 *X* 是一个矩阵，返回一个向量。
- 如果 *X* 是一张表，返回一张表。

## 例子

```dolphindb
last(`hello `world);
```

输出返回：world

```dolphindb
last(1..10);
```

输出返回：10

```dolphindb
m = matrix(1 2 3, 4 5 6);
m;
```

输出返回：

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
last(m);
```

输出返回：[3,6]

相关函数：[first](../f/first.html)
