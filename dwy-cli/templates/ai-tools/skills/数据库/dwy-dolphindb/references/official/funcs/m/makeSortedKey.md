---
source_url: https://docs.dolphindb.cn/zh/funcs/m/makeSortedKey.html
fetched_at: 2026-05-19T09:30:48Z
category: funcs
title: makeSortedKey
sha1: 0522d897969f4d89d2b35fd28b9f3478811da7e5
---

# makeSortedKey

## 语法

`makeSortedKey(args...)`

## 详情

对于输入的多个 *args*，将它们的值组合为一个 BLOB 标量或向量。相较于
`makeKey`，`makeSortedKey` 内部会保存组合值的排序结果，但输出结果与
`makeKey` 相同。

## 参数

**args** 是多个标量或长度相同的向量。

## 返回值

BLOB 标量或向量。

## 例子

```dolphindb
makeSortedKey([`b,`a,`c], [`4,`2,`1])
// output: ["b4","a2","c1"]

set(makeSortedKey(1 2, 4 5))
```
