---
source_url: https://docs.dolphindb.cn/zh/funcs/e/expm1.html
fetched_at: 2026-05-19T09:21:28Z
category: funcs
title: expm1
sha1: 1626f2ad81a2ce228f9b63f214e64d405d013b16
---

# expm1

## 语法

`expm1(X)`

## 详情

返回 exp(X)-1 的结果。

DolphinDB 的 `expm1` 与 NumPy 的 `expm1` 在核心功能上是一致的，但
DolphinDB `expm1` 强调向量化和分布式计算能力，而 NumPy 作为通用数值计算库，其函数基于 ufunc
机制，提供了更丰富的底层控制参数，例如：

- *out*：支持将结果写入指定数组，实现原地计算
- *where*：支持按条件进行选择性计算
- *dtype*：控制计算和输出的数据类型
- *casting*：控制类型转换规则
- *order*：指定输出数组的内存布局
- *subok*：控制是否保留子类类型

需要注意的是，这些参数并非 `expm1` 特有，而是 NumPy ufunc 的通用特性。

## 参数

**X** 可以是标量、数据对、向量、矩阵或表。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
expm1(5);
// output
147.413159

expm1(1 2 3 NULL);
// output
[1.718282,6.389056,19.085537,]

expm1(1..4$2:2);
```

| #0 | #1 |
| --- | --- |
| 1.718282 | 19.085537 |
| 6.389056 | 53.59815 |
