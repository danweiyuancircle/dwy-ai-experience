---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cbrt.html
fetched_at: 2026-05-19T09:14:34Z
category: funcs
title: cbrt
sha1: 2b46bc6938249fbc1069db874586d2ffd3d8f3ab
---

# cbrt

## 语法

`cbrt(X)`

## 详情

返回 *X* 的立方根。

注：

与 [numpy.cbrt](https://numpy.org/doc/stable/reference/generated/numpy.cbrt.html) 函数的核心功能相同，区别在于 DolphinDB 中
`cbrt` 函数只接受一个参数 *X*，不支持 `numpy.cbrt` 中的
*out*、*where*、*dtype*、*casting* 和 *order* 等参数。

## 参数

**X** 可以是标量、数据对、向量、矩阵或表。

## 返回值

DOUBLE 类型，数据形式同 *X*。

## 例子

```dolphindb
cbrt(8);
// output
2

cbrt(8 12 16);
// output
[2,2.289428,2.519842]

cbrt(1..6$2:3);
```

| 0 | 1 | 2 |
| --- | --- | --- |
| 1 | 1.44225 | 1.709976 |
| 1.259921 | 1.587401 | 1.817121 |
