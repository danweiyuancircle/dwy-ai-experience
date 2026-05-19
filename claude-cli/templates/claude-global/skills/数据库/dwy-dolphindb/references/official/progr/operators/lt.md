---
source_url: https://docs.dolphindb.cn/zh/progr/operators/lt.html
fetched_at: 2026-05-19T09:01:18Z
category: progr
title: lt(<)
sha1: 2fec01a342848a96f2658678819fef8a64771ade
---

# lt(<)

## 语法

`X<Y`

## 参数

**X** 和 **Y** 可以是标量、数据对、向量、矩阵或集合。当X和Y都是向量或矩阵时，它们的长度或维度必须相同。

## 详情

- 如果X和Y都不是集合，则对X和Y中的元素逐个做<的比较并返回结果。
- 如果X和Y是集合，检查X是否为Y的真子集。

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

集合运算： 如果X<Y，那么 X是Y的真子集。

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
// x是y的真子集

y<x;
// output
0
// y不是x的真子集

x<x;
// output
0
// x不是x的真子集
```
