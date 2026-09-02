---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isMonotonicDecreasing.html
fetched_at: 2026-05-19T09:28:35Z
category: funcs
title: isMonotonicDecreasing
sha1: 38c89f93ca352e69ec5dbb898c3f7ace167c6bdf
---

# isMonotonicDecreasing

## 语法

`isMonotonicDecreasing(X)`

## 详情

判断 *X* 是否为单调递减。

## 参数

**X** 可以是标量或向量。

## 返回值

布尔型标量或向量。

## 例子

```dolphindb
a=[10,7,5,2,int()];
isMonotonicDecreasing(a);
// output: true

a=[10.5,8.7,int(),5.3,1.0];
isMonotonicDecreasing(a);
// output: false

a=[5,10,14,20,int()];
isMonotonicDecreasing(a);
// output: false
```

相关函数：[isMonotonicIncreasing](isMonotonicIncreasing.html), [isMonotonic](isMonotonic.html)
