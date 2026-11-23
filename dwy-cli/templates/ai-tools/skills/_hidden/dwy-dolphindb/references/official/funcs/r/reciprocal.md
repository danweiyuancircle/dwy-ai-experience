---
source_url: https://docs.dolphindb.cn/zh/funcs/r/reciprocal.html
fetched_at: 2026-05-19T09:35:27Z
category: funcs
title: reciprocal
sha1: a5773ff37d82bb9459afa60b40c9c4dcf8eeb280
---

# reciprocal

## 语法

`reciprocal(X)`

## 详情

返回 *X* 的倒数。

DolphinDB 的 `reciprocal` 与 NumPy 的 `numpy.reciprocal`
在数学意义上相同，但对整数输入的处理不同。NumPy 会保持整数类型，因此 1/2 会得到 0；而 DolphinDB 会自动转换为浮点计算，返回 0.5。
例如，`reciprocal([1, 2, 4])` 的结果为 `[1,0.5,0.25]`，而
`np.reciprocal([1, 2, 4])` 的结果为 `[1,0,0]`。若 NumPy
使用浮点类型数据作为输入，则结果与 DolphinDB 相同。

## 参数

**X** 可以是数值型标量、向量或矩阵。

## 返回值

返回结果为 DOUBLE 类型。

## 例子

```dolphindb
reciprocal(10);
// output: 0.1

reciprocal(1 2 4 8);
// output: [1,0.5,0.25,0.125]

reciprocal(1 2 4 8$2:2);
```

| #0 | #1 |
| --- | --- |
| 1 | 0.25 |
| 0.5 | 0.125 |
