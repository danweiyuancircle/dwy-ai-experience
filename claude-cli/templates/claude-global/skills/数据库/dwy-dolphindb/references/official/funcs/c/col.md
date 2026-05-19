---
source_url: https://docs.dolphindb.cn/zh/funcs/c/col.html
fetched_at: 2026-05-19T09:15:31Z
category: funcs
title: col
sha1: 2f0c67075d0a5b83466723082cad21354cfd25eb
---

# col

## 语法

`col(obj, index)` 或 `column(obj,
index)`

## 详情

返回向量、矩阵或表的一列或多列。参见相关函数：[row](../r/row.html)。

## 参数

**obj** 可以是向量、矩阵或表。

**index** 是一个整数标量或数据对。

## 返回值

返回一个与输入 *obj* 相同数据类型和形式的对象。

## 例子

```dolphindb
x=1..6$3:2;
x;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
col(x,0);
// output
[1,2,3]

x.col(1);
// output
[4,5,6]

a=table(1..3 as x,`IBM`C`AAPL as y);
a;
```

| x | y |
| --- | --- |
| 1 | IBM |
| 2 | C |
| 3 | AAPL |

```dolphindb
a col 1;
// output
["IBM","C","AAPL"]

col(a, 0:2)
```

| x | y |
| --- | --- |
| 1 | IBM |
| 2 | C |
| 3 | AAPL |
