---
source_url: https://docs.dolphindb.cn/zh/funcs/r/row.html
fetched_at: 2026-05-19T09:36:42Z
category: funcs
title: row
sha1: 4b8a3349014a24ea9cfd3cdcaab6b75b5761f614
---

# row

## 语法

`row(obj,index)`

## 详情

获取向量、矩阵或表的一行或多行。参见相关函数：[col](../c/col.html)。

## 参数

**obj** 可以是向量、矩阵或表

**index** 是一个整数标量或数据对。

## 返回值

返回向量、矩阵或表的一行或多行。

## 例子

```dolphindb
x=matrix(1 2 3, 4 5 6);
x;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
row(x,1);
// output
[2,5]

row(x,0);
// output
[1,4]

x.row(2);
// output
[3,6]

a=table(1..3 as x,`IBM`C`AAPL as y);
a
```

| x | y |
| --- | --- |
| 1 | IBM |
| 2 | C |
| 3 | AAPL |

```dolphindb
row(a,1);
// output
y->C
x->2

row(a,1:3)
```

| x | y |
| --- | --- |
| 2 | C |
| 3 | AAPL |
