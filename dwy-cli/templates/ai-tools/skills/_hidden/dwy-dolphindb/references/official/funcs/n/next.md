---
source_url: https://docs.dolphindb.cn/zh/funcs/n/next.html
fetched_at: 2026-05-19T09:33:13Z
category: funcs
title: next
sha1: 1f891d57d75f98e25ecafca5fc9fa46a6f499fa2
---

# next

## 语法

`next(X)`

## 详情

将 *X* 向左移动一个位置。类似地：[prev](../p/prev.html) 将
*X* 向右移动一个位置；[move](../m/move.html) 可以将 *X*向左或向右移动一个位置。

与Python 中 next 的区别：Python 的 next 函数用于从迭代器中取下一个元素，DolphinDB 中 `next(X)`
相当于 Python 中的 `shift(X, -1)`。

## 参数

**X** 可以是向量、矩阵或表。

## 返回值

返回一个与输入 *X*  相同数据类型和形式的对象。

## 例子

```dolphindb
x = 1..5;
next(x);
// output: [2,3,4,5,]
```

```dolphindb
x = matrix(1 2 3 4 5);
next(x)
```

| #0 |
| --- |
| 2 |
| 3 |
| 4 |
| 5 |
|  |

```dolphindb
t=table(1 2 3 as a, `x`y`z as b, 10.8 7.6 3.5 as c);
next(t)
```

| a | b | c |
| --- | --- | --- |
| 2 | y | 7.6 |
| 3 | z | 3.5 |
|  |  |  |
