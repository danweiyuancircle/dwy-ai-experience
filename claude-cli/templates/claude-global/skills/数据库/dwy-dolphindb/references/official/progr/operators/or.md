---
source_url: https://docs.dolphindb.cn/zh/progr/operators/or.html
fetched_at: 2026-05-19T09:01:26Z
category: progr
title: or(||)
sha1: 7b4c29c4d239c5b283390f580409ac356f737b21
---

# or(||)

## 语法

`X || Y`

## 参数

**X** 和 **Y** 可以是标量、数据对、向量或矩阵。当X和Y都是向量或矩阵时，它们的长度必须相同。

## 详情

返回X和Y中每一个元素逻辑或(||)的结果。若操作数包含 NULL，则返回的对应结果也是 NULL。

## 例子

```dolphindb
1 || 0;
// output
1

x=1 0 1;
x || 0;
// output
[1,0,1]

y=0 1 0;
x or y;
// output
[1,1,1]

m1=1 1 1 0 0 0$2:3;
m1;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 1 | 0 |
| 1 | 0 | 0 |

```dolphindb
m1 || 0;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 1 | 0 |
| 1 | 0 | 0 |

```dolphindb
m2=1 0 1 0 1 0$2:3;
m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 1 | 1 |
| 0 | 0 | 0 |

```dolphindb
or(m1, m2);
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 1 | 1 |
| 1 | 0 | 0 |

```dolphindb
t=table(1..3 as id, 4..6 as value);
t;
```

| id | value |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
select id, value from t where id=2 or id=3;
```

| id | value |
| --- | --- |
| 2 | 5 |
| 3 | 6 |
