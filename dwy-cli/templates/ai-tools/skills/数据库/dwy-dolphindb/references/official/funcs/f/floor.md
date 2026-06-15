---
source_url: https://docs.dolphindb.cn/zh/funcs/f/floor.html
fetched_at: 2026-05-19T09:21:50Z
category: funcs
title: floor
sha1: 35de313f1e2a23a018f83d7f70d6feadea540595
---

# floor

## 语法

`floor(X)`

## 详情

`floor` 和 [ceil](../c/ceil.html)
函数分别把一个实数映射到小于等于它的最大整数，和大于等于它的最小整数。函数 [round](../r/round.html)
根据四舍五入规则把一个实数映射到最接近的整数。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

整型标量、向量或矩阵。

## 例子

```dolphindb
floor(2.1);
// output
2
floor(2.9);
// output
2
floor(-2.1);
// output
-3

ceil(2.1);
// output
3
ceil(2.9);
// output
3
ceil(-2.1);
// output
-2

round(2.1);
// output
2
round(2.9);
// output
3
round(-2.1);
// output
-2

m = 1.1 2.2 3.3 4.4 5.5 6.6 7.7 8.8 9.9 10$2:5;
m;
```

| #0 | #1 | #2 | #3 | #4 |
| --- | --- | --- | --- | --- |
| 1.1 | 3.3 | 5.5 | 7.7 | 9.9 |
| 2.2 | 4.4 | 6.6 | 8.8 | 10 |

```dolphindb
floor(m);
```

| #0 | #1 | #2 | #3 | #4 |
| --- | --- | --- | --- | --- |
| 1 | 3 | 5 | 7 | 9 |
| 2 | 4 | 6 | 8 | 10 |
