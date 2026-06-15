---
source_url: https://docs.dolphindb.cn/zh/funcs/p/prev.html
fetched_at: 2026-05-19T09:34:29Z
category: funcs
title: prev
sha1: c6ca5df49a039457aaf3ebeabc926b2088d4b511
---

# prev

## 语法

`prev(X)`

## 详情

将 *X* 向右移动一个位置。类似地：[next](../n/next.html) 将
*X* 向左移动一个位置；[move](../m/move.html) 可以将 *X*向左或向右移动一个位置。

## 参数

**X** 可以是向量、矩阵或表。

## 返回值

一个向量、矩阵或表。

## 例子

```dolphindb
x=3 9 5 1 4;
prev(x);
// output: [,3,9,5,1]
```

```dolphindb
x = matrix(1 2 3 4 5);
prev(x)#0
```

| #0 |
| --- |
|  |
| 1 |
| 2 |
| 3 |
| 4 |

```dolphindb
t=table(1 2 3 as a, `x`y`z as b, 10.8 7.6 3.5 as c);
prev(t)
```

| a | b | c |
| --- | --- | --- |
|  |  |  |
| 1 | x | 10.8 |
| 2 | y | 7.6 |
