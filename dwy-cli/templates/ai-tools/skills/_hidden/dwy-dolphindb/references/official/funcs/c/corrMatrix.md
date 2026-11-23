---
source_url: https://docs.dolphindb.cn/zh/funcs/c/corrMatrix.html
fetched_at: 2026-05-19T09:15:57Z
category: funcs
title: corrMatrix
sha1: dafc982e62e7b18ba900088373a3f907651e2b0b
---

# corrMatrix

## 语法

`corrMatrix(X)`

## 详情

设矩阵 *X* 有 n 列，将其每一列作为一维向量，求 n 维向量的相关矩阵（correlation matrix）。

注：

- 如果矩阵中含有空值，会默认将空值转化为0，然后进行计算。而由于 [corr](corr.html)
  函数计算时忽略 NULL 值，因此调用 [cross/pcross(corr, X)](../ho_funcs/cross.html) 函数计算相关矩阵时也会忽略 NULL 值。
- 在不含 NULL 值的情况下，虽然该函数计算结果等价于 `cross(corr,
  X)`，但该函数内部进行了优化，其性能较 [cross/pcross(corr, X)](../ho_funcs/cross.html) 函数有大幅提升。

## 参数

**X** 是一个矩阵。

## 返回值

DOUBLE 类型矩阵。

## 例子

```dolphindb
m = rand(10.0, 30)$10:3
corrMatrix(m)
```

输出返回：

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 0.167257129736134 | 0.224955585716037 |
| 0.167257129736134 | 1 | -0.12066768907057 |
| 0.224955585716037 | -0.12066768907057 | 1 |

```dolphindb
a = rand(1.0, 30000000).reshape(10000:3000)
a.rename!("s" + string(1..3000))
timer corrMatrix(a)
```

输出返回：Time elapsed: 2986.932 ms

```dolphindb
timer pcross(corr, a)
```

输出返回：Time elapsed: 45629.6 ms

相关函数： [covarMatrix](covarMatrix.html)
