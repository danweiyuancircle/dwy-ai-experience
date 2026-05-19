---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setRandomSeed.html
fetched_at: 2026-05-19T09:38:59Z
category: funcs
title: setRandomSeed
sha1: 23184df9ecc2228e68c9202aba9c601cec42d98d
---

# setRandomSeed

## 语法

`setRandomSeed(seed)`

## 详情

设置随机数种子。

## 参数

**seed** 是一个整数，表示随机数种子。

## 例子

```dolphindb
setRandomSeed(5);
rand(10, 10);
```

输出返回：[2,0,8,8,2,3,9,9,4,0]
