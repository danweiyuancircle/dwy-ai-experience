---
source_url: https://docs.dolphindb.cn/zh/funcs/i/imax.html
fetched_at: 2026-05-19T09:27:32Z
category: funcs
title: imax
sha1: 833203f8c6765d7778dc4c6f1f1ae6541c614282
---

# imax

## 语法

`imax(X)`

## 详情

查找数据中最大值的位置索引，如果有多个相同的最大值，返回第一个（最左）的位置。位置索引从 0 开始计数。空向量返回 -1。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

- 若 *X* 是标量或向量，返回一个整型标量。
- 若 *X* 为矩阵，返回一个向量。
- 若 *X* 为表，返回一个表。

## 例子

```dolphindb
x = 1.2 2 NULL 6 -1 6;
imax(x);
// 输出：3

x = 5 3 1 6 4 6 $ 3:2;
imax(x);
// 输出：(0,0)

x=array(INT,0);
x;
// 输出：[]

imax(x);
// 输出：-1
// 对于一个空向量，imax 返回 -1

m=matrix(1 2 3, 6 5 4);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 6 |
| 2 | 5 |
| 3 | 4 |

```dolphindb
imax(m);
// 输出：[2,0]
```

相关函数：[imaxLast](imaxlast.html)
