---
source_url: https://docs.dolphindb.cn/zh/funcs/m/makeKey.html
fetched_at: 2026-05-19T09:30:46Z
category: funcs
title: makeKey
sha1: e64abede4ea0a1efd9bdeb64956f5a158bd61a4b
---

# makeKey

## 语法

`makeKey(args...)`

## 详情

对于输入的多个 *args*，将它们的值组合为一个 BLOB 标量或向量。返回的结果可用作字典或集合的 key。相较于
`makeSortedKey`，`makeKey` 不会保存组合值的排序结果。

## 参数

**args** 是多个标量或长度相同的向量。

## 返回值

BLOB 标量或向量。

## 例子

```dolphindb
makeKey(`a1,`b1,`c1)
// output: a1b1c1

set(makeKey(1 2, 4 5))

re=makeKey(`a1`a2, `_1`_2)
dict(re,100 200)

// output
a2_2->200
a1_1->100
```

相关函数：[makeSortedKey](makeSortedKey.html)
