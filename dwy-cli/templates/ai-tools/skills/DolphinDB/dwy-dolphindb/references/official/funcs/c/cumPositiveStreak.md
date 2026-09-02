---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumPositiveStreak.html
fetched_at: 2026-05-19T09:17:41Z
category: funcs
title: cumPositiveStreak
sha1: 966d9d15eced8eb4c478f35c9d597f0bf2a7c66f
---

# cumPositiveStreak

## 语法

`cumPositiveStreak(X)`

参数说明和窗口计算规则请参考：[cumFunctions](../themes/cumFunctions.html)

## 详情

累计计算 *X* 中连续的正数之和的。

## 返回值

LONG/DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x=1 0 -1 1 2 2 2 1 0 -1 0 2;

cumPositiveStreak x;
// output
[1,0,0,1,3,5,7,8,0,0,0,2]

m=matrix(1 0 -1 1 2 2 2 1 0 -1 0 2, -1 -2 -1 0 1 3 6 7 0 -1 -2 0);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | -1 |
| 0 | -2 |
| -1 | -1 |
| 1 | 0 |
| 2 | 1 |
| 2 | 3 |
| 2 | 6 |
| 1 | 7 |
| 0 | 0 |
| -1 | -1 |
| 0 | -2 |
| 2 | 0 |

```dolphindb
cumPositiveStreak(m);
```

| #0 | #1 |
| --- | --- |
| 1 | 0 |
| 0 | 0 |
| 0 | 0 |
| 1 | 0 |
| 3 | 1 |
| 5 | 4 |
| 7 | 10 |
| 8 | 17 |
| 0 | 0 |
| 0 | 0 |
| 0 | 0 |
| 2 | 0 |
