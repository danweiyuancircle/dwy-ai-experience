---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isMonotonicIncreasing.html
fetched_at: 2026-05-19T09:28:36Z
category: funcs
title: isMonotonicIncreasing
sha1: 1cc282613da518bdef08e3233e15b8824d2747bc
---

# isMonotonicIncreasing

## 语法

`isMonotonicIncreasing(X)`

## 详情

判断 *X* 是否为单调递增。

## 参数

**X** 可以是标量或向量。

## 返回值

布尔型标量或向量。

## 例子

```dolphindb
a=[int(),2,5,7,10]
isMonotonicIncreasing(a);
// output: true

a=[2.1,double(),3.5,4.7,8.2,10.5]
isMonotonicIncreasing(a);
// output: false

a=[5,10,14,20,int()]
isMonotonicIncreasing(a);
// output: false
```

相关函数：[isMonotonicDecreasing](isMonotonicDecreasing.html), [isMonotonic](isMonotonic.html)
