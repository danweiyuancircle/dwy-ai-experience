---
source_url: https://docs.dolphindb.cn/zh/funcs/i/inverse.html
fetched_at: 2026-05-19T09:27:59Z
category: funcs
title: inverse
sha1: 7857ab8381cfcbc9811b4694dabec510bb82a334
---

# inverse

## 语法

`inverse(X)`

## 详情

如果 *X* 可逆，返回矩阵 *X* 的逆矩阵。

## 参数

**X** 是一个矩阵。

## 返回值

如果 *X* 可逆，返回矩阵 *X* 的逆矩阵。否则报错。

## 例子

```dolphindb
x=1..4$2:2;
x;
```

| #0 | #1 |
| --- | --- |
| 1 | 3 |
| 2 | 4 |

```dolphindb
x.inverse();
```

| #0 | #1 |
| --- | --- |
| -2 | 1.5 |
| 1 | -0.5 |
