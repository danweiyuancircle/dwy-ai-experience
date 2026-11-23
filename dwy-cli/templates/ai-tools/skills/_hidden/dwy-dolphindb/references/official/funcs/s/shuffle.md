---
source_url: https://docs.dolphindb.cn/zh/funcs/s/shuffle.html
fetched_at: 2026-05-19T09:39:19Z
category: funcs
title: shuffle
sha1: d81236a05ed9844e68d392811bf11355cf32225c
---

# shuffle

## 语法

`shuffle(X)`

shuffle! 是 `shuffle`
的原地计算的版本。

## 详情

对数据重组后，返回一个新的向量或矩阵。

## 参数

**x** 可以是向量或矩阵。

## 返回值

数据重组后，返回一个新的向量或矩阵。

## 例子

```dolphindb
x=(1..6).shuffle();
x;
// output
[1,6,3,5,4,2]

x.shuffle!();
// output
[5,4,1,3,2,6]

x=(1..6).reshape(3:2);
x;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
x.shuffle();
```

| #0 | #1 |
| --- | --- |
| 5 | 3 |
| 2 | 1 |
| 4 | 6 |
