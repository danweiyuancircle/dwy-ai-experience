---
source_url: https://docs.dolphindb.cn/zh/funcs/r/repmat.html
fetched_at: 2026-05-19T09:36:06Z
category: funcs
title: repmat
sha1: 4e05679bf9207d48d5d6c7c1a716522c72fbd793
---

# repmat

## 语法

`repmat(X, rowRep, colRep)`

## 详情

将矩阵 *X* 竖向重复 *rowRep* 次，横向重复 *colRep*
次，产生一个新的矩阵。

## 参数

**X** 是一个矩阵。

**rowRep** 与 **colRep** 均为正整数。

## 返回值

一个矩阵。

## 例子

```dolphindb
x=matrix(1 2 3, 4 5 6);
```

输出返回：

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
repmat(x, 2, 3);
```

输出返回：

| #0 | #1 | #2 | #3 | #4 | #5 |
| --- | --- | --- | --- | --- | --- |
| 1 | 4 | 1 | 4 | 1 | 4 |
| 2 | 5 | 2 | 5 | 2 | 5 |
| 3 | 6 | 3 | 6 | 3 | 6 |
| 1 | 4 | 1 | 4 | 1 | 4 |
| 2 | 5 | 2 | 5 | 2 | 5 |
| 3 | 6 | 3 | 6 | 3 | 6 |
