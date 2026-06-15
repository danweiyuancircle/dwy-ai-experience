---
source_url: https://docs.dolphindb.cn/zh/funcs/x/xor.html
fetched_at: 2026-05-19T09:44:20Z
category: funcs
title: xor
sha1: 04ae63e3ad380400d9a0c1fd9ed504b781819b0a
---

# xor

## 语法

`xor(X, Y)`

## 详情

按元素逐个返回 *X* 逻辑异或 (`XOR`)*Y* 的结果。

## 参数

**X** 和 **Y** 可以是标量、数据对、向量、矩阵或表。

## 返回值

布尔型标量、数据对、向量、矩阵或表，表示 *X* 逻辑异或 *Y* 的结果。

## 例子

```dolphindb
1 xor 0
// output: true

x = 5 6 7
x xor 0
// output: [true,true,true]

x = 1 2 3
y = 2 1 3
x xor y
// output: [false,false,false]

true xor false
// output: true
```

相关函数：[or](../o/or.html), [not](../n/not.html)
