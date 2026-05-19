---
source_url: https://docs.dolphindb.cn/zh/progr/operators/neg.html
fetched_at: 2026-05-19T09:01:24Z
category: progr
title: neg(-)
sha1: 3e95467dcd28c5bd3227a664e9a0e88d13e21e57
---

# neg(-)

## 语法

`X`

## 参数

**X** 可以是标量、数据对、向量或矩阵。

## 详情

返回X的负数。

## 例子

```dolphindb
x=1:2;
-x;
// output
-1 : -2

x=1 0 1;
-x;
// output
[-1,0,-1]

m=1 1 1 0 0 0 $ 2:3;
m;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 1 | 0 |
| 1 | 0 | 0 |

```dolphindb
-m;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| -1 | -1 | 0 |
| -1 | 0 | 0 |
