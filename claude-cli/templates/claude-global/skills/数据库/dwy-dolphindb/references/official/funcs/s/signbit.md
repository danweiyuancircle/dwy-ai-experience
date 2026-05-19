---
source_url: https://docs.dolphindb.cn/zh/funcs/s/signbit.html
fetched_at: 2026-05-19T09:39:20Z
category: funcs
title: signbit
sha1: 673d13c01ea5d999a635ffc721b478b15b7a935e
---

# signbit

## 语法

`signbit(X)`

## 详情

获取输入数据的符号位。

注：

DolphinDB `signbit` 与 [numpy.signbit](https://numpy.org/doc/stable/reference/generated/numpy.signbit.html) 的核心功能相同。区别在于：

- DolphinDB `signbit` 主要面向浮点数或整数标量，复数可通过
  `lowDouble` 和 `highDouble` 分别检测实部和虚部。
- `numpy.signbit` 支持标量和数组逐元素计算，并支持更多参数，如
  *out*、*where*。

## 参数

**X**：一个整型或者浮点型的标量。

## 返回值

负号返回 true；正号返回 false。

## 例子

```dolphindb
signbit('a')
false

signbit(-21)
true

signbit(-2.1)
true

b=complex(10,-5)//创建一个复数
b
10.0-5.0i
signbit(highDouble(b)) //判断虚部符号
true

signbit(lowDouble(b))  //判断实部符号
false
```
