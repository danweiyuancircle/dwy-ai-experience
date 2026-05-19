---
source_url: https://docs.dolphindb.cn/zh/funcs/r/reshape.html
fetched_at: 2026-05-19T09:36:14Z
category: funcs
title: reshape
sha1: f27b69820062d223e642e2e5bf88b337c709b5b8
---

# reshape

## 语法

`reshape(obj, [dim])`

## 详情

改变矩阵的形状。如果没有指定 *dim*，则将 *obj* 重组为一个向量。

DolphinDB 的 `reshape(obj, dim)` 与 NumPy 的 `numpy.reshape(a,
shape)` 都用于调整数据形状，但两者在行为上存在差异：

- DolphinDB 仅支持向量和矩阵，目标维度通过数据对指定，并默认按列优先填充，行为更接近 NumPy 的
  `order="F"`。
- NumPy 支持任意维度的 ndarray，默认按行优先（`order="C"`）填充，同时支持自动推断维度，以及
  *order*、*copy* 等参数。
- 此外，DolphinDB 在省略 `dim` 时会将矩阵展平成向量；而 NumPy 必须显式指定目标形状，通常使用
  `reshape(-1)` 实现展平操作。

## 参数

**obj** 是一个向量或矩阵。

**dim** 是一个数据对，表示返回结果的行数和列数。它是一个可选参数。

## 返回值

返回一个改变形状后的矩阵。如果没有指定 *dim*，则返回一个向量。

## 例子

```dolphindb
x=1..6;
x=x.reshape(3:2);
x
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
x=x.reshape(2:3);
x
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 5 |
| 1 | 4 | 6 |

```dolphindb
x=x.reshape(6:1)
x
```

| #0 |
| --- |
| 1 |
| 2 |
| 3 |
| 4 |
| 5 |
| 6 |

```dolphindb
x.reshape()
// output
[1,2,3,4,5,6]    // 将 x 重组为一个向量
```
