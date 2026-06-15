---
source_url: https://docs.dolphindb.cn/zh/funcs/t/type.html
fetched_at: 2026-05-19T09:43:01Z
category: funcs
title: type
sha1: 7e0ddcb2f499ac2d3efbcea824ba3c8b468979ba
---

# type

## 语法

`type(X)`

## 详情

返回一个表明 *X* 的数据类型的整数。详细信息参见 [数据类型](../../progr/data_types.html)。

## 参数

**X** 可以是系统支持的任意数据类型。

## 返回值

INT 类型标量。

## 例子

```dolphindb
x=3;
x;
// output
3

type(x);
// output
4
// INT

type(1.2);
// output
16
// DOUBLE

type("Hello");
// output
18
// STRING
```
