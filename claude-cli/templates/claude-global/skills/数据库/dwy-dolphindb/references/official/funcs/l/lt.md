---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lt.html
fetched_at: 2026-05-19T09:30:37Z
category: funcs
title: lt
sha1: 18283b7118f469d96ed43ab9a2ce34496fe4670b
---

# lt

## 语法

`lt(X, Y)` 或 `X<Y`

## 详情

如果 *X* 和 *Y* 都不是集合，返回逐个元素比较 *X*<*Y*
的结果。

如果 *X* 和 *Y* 都是集合，则检查 *X* 是否为 *Y* 的真子集。

## 参数

**X** 和 **Y** 可以是标量、数据对、向量、矩阵或集合。如果 *X* 或 *Y*
中的其中一个是数据对、向量或矩阵，另一个必须是一个标量，或具有相同长度或维度的数据对、向量或矩阵。

## 返回值

返回布尔类型的标量、向量、数据对或矩阵。

## 例子

```dolphindb
1 2 3 < 2;
// output
[1,0,0]

1 2 3<0 2 4;
// output
[0,0,1]

2:3<1:6;
// output
0 : 1

m1=1..6$2:3;
m1;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 5 |
| 2 | 4 | 6 |

```dolphindb
m1 lt 4;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 1 | 0 |
| 1 | 0 | 0 |

```dolphindb
m2=6..1$2:3;
m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 6 | 4 | 2 |
| 5 | 3 | 1 |

```dolphindb
m1<m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 1 | 0 |
| 1 | 0 | 0 |

集合操作：如果 *X*<*Y*，则 *X* 是 *Y* 的真子集。

```dolphindb
x=set(4 6);
x;
// output
set(6,4)
y=set(8 9 4 6);
y;
// output
set(6,4,9,8)

x<y;
// output
1

y<x;
// output
0

x<x;
// output
0
# x is not a proper subset of x
```
