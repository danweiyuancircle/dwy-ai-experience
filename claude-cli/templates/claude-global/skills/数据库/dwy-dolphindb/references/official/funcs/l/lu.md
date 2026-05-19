---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lu.html
fetched_at: 2026-05-19T09:30:40Z
category: funcs
title: lu
sha1: f5c1075c95efddb4a4078e76243ce5d601288752
---

# lu

## 语法

`lu(obj, [permute=false])`

## 详情

实现矩阵的 LU 分解。

注：

DolphinDB `lu` 与 [scipy.linalg.lu](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html) 的核心功能相同，区别在于
`scipy.linalg.lu` 支持更多参数，如
*overwrite\_a*、*check\_finite*、*p\_indices*。

## 参数

**obj** 是一个不包含 NULL 值的矩阵。

**permute** 是一个布尔值。默认值为 false。

## 返回值

- 如果 *permute* 为 false，返回三个矩阵，依次是 L, U, P，满足条件 *obj* = P' \* L \* U。P
  是置换矩阵；L 是下三角矩阵，其对角线元素均为1；U 是上三角矩阵。
- 如果 *permute* 为 true，返回两个矩阵，依次是 L,U，满足条件 *obj* = L \* U。

## 例子

```dolphindb
A = matrix([[2, 5, 8, 7], [5, 2, 2, 8], [7, 5, 6, 6], [5, 4, 4, 8]]);

P, L, U = lu(A);
P;
```

| #0 | #1 | #2 | #3 |
| --- | --- | --- | --- |
| 0 | 0 | 1 | 0 |
| 0 | 0 | 0 | 1 |
| 1 | 0 | 0 | 0 |
| 0 | 1 | 0 | 0 |

```dolphindb
L;
```

| #0 | #1 | #2 | #3 |
| --- | --- | --- | --- |
| 1 | 0 | 0 | 0 |
| 0.875 | 1 | 0 | 0 |
| 0.25 | 0.72 | 1 | 0 |
| 0.625 | 0.12 | 0.233871 | 1 |

```dolphindb
U;
```

| #0 | #1 | #2 | #3 |
| --- | --- | --- | --- |
| 8 | 2 | 6 | 4 |
| 0 | 6.25 | 0.75 | 4.5 |
| 0 | 0 | 4.96 | 0.76 |
| 0 | 0 | 0 | 0.782258 |

```dolphindb
L, U = lu(A, true);
L;
```

| #0 | #1 | #2 | #3 |
| --- | --- | --- | --- |
| 0.25 | 0.72 | 1 | 0 |
| 0.625 | 0.12 | 0.233871 | 1 |
| 1 | 0 | 0 | 0 |
| 0.875 | 1 | 0 | 0 |

```dolphindb
U;
```

| #0 | #1 | #2 | #3 |
| --- | --- | --- | --- |
| 8 | 2 | 6 | 4 |
| 0 | 6.25 | 0.75 | 4.5 |
| 0 | 0 | 4.96 | 0.76 |
| 0 | 0 | 0 | 0.782258 |
