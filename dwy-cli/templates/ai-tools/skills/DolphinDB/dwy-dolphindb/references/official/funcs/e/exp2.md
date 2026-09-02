---
source_url: https://docs.dolphindb.cn/zh/funcs/e/exp2.html
fetched_at: 2026-05-19T09:21:27Z
category: funcs
title: exp2
sha1: 22dc43bb9d9d6591357e87998f4cfdd2a6c2e168
---

# exp2

## 语法

`exp2(X)`

## 详情

返回2的 *X* 次方。

## 参数

**X** 可以是标量、数据对、向量、矩阵或表。

DolphinDB 的 `exp2` 与 NumPy 的 `exp2` 在核心功能上是一致的，但
DolphinDB `exp2` 强调向量化和分布式计算能力，而 NumPy 作为通用数值计算库，其函数基于 ufunc
机制，提供了更丰富的底层控制参数，例如：

- *out*：支持将结果写入指定数组，实现原地计算
- *where*：支持按条件进行选择性计算
- *dtype*：控制计算和输出的数据类型
- *casting*：控制类型转换规则
- *order*：指定输出数组的内存布局
- *subok*：控制是否保留子类类型

需要注意的是，这些参数并非 `exp2` 特有，而是 NumPy ufunc 的通用特性。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
exp2(3);
// output
8

exp2(2 4 NULL 6);
// output
[4,16,,64]

exp2(1..4$2:2);
```

| #0 | #1 |
| --- | --- |
| 2 | 8 |
| 4 | 16 |
