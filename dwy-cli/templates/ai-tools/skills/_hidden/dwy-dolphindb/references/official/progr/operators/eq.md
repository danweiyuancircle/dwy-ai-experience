---
source_url: https://docs.dolphindb.cn/zh/progr/operators/eq.html
fetched_at: 2026-05-19T09:01:10Z
category: progr
title: eq(==)
sha1: e09ebd56bb6caea8de9b4004c83bf619d63e1dc1
---

# eq(==)

## 语法

`X==Y`

## 参数

**X** 和 **Y** 可以是标量、数据对、向量、矩阵或集合。当 *X* 和 *Y* 都是向量或矩阵时，它们的长度或维度必须相同。

## 详情

- 如果X和Y都不是集合，则对X和Y中的元素逐个比较是否相等并返回结果。
- 如果X和Y是集合，则检查X和Y是否相同。

## 例子

```dolphindb
1 2 3 == 2;
// output
[0,1,0]

1 2 3==0 2 4;
// output
[0,1,0]

1:2==1:6;
// output
1 : 0

m1=1..6$2:3;
m1;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 5 |
| 2 | 4 | 6 |

```dolphindb
m1 == 4;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 0 | 0 | 0 |
| 0 | 1 | 0 |

```dolphindb
m2=6..1$2:3;
m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 6 | 4 | 2 |
| 5 | 3 | 1 |

```dolphindb
m1==m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 0 | 0 | 0 |
| 0 | 0 | 0 |

集合运算：如果X==Y 那么 X和Y就是相同的。

```dolphindb
x=set(4 6);
y=set(4 6 8);

x==y;
// output
0
x==x;
// output
1
```
