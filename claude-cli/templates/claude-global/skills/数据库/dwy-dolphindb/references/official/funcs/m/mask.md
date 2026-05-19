---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mask.html
fetched_at: 2026-05-19T09:30:52Z
category: funcs
title: mask
sha1: 49603910c8486be6b01ae35a596a58732b9dfc79
---

# mask

## 语法

`mask(X, Y)`

## 详情

对 *X* 中每个元素应用条件 *Y*。若结果为 false，保留该元素。若结果为 true，将其替换为
NULL。

## 参数

**X** 是一个标量、向量或矩阵。

**Y** 是一个布尔表达式。

## 返回值

返回一个与 *X* 一致的对象（标量返回标量，向量返回同长向量，矩阵返回同形矩阵）。

## 例子

```dolphindb
x=1..10
mask(x, x>6);
// output: [1,2,3,4,5,6,,,,]

m=matrix(1 2 3, 4 5 6, 7 8 9);
m;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 4 | 7 |
| 2 | 5 | 8 |
| 3 | 6 | 9 |

```dolphindb
mask(m, m<6);
```

| #0 | #1 | #2 |
| --- | --- | --- |
|  |  | 7 |
|  |  | 8 |
|  | 6 | 9 |
