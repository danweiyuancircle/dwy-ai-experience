---
source_url: https://docs.dolphindb.cn/zh/funcs/d/drop.html
fetched_at: 2026-05-19T09:19:14Z
category: funcs
title: drop
sha1: 2f426ee315201e334ad14e0e62e8239e773805b0
---

# drop

## 语法

`drop(obj, count)`

## 详情

从向量/矩阵/表中删除前/后指定个数的元素/列/行。

## 参数

**obj** 可以是向量、矩阵或表。

**count** 是一个整数，表示要删除的个数，为负数时表示从后开始删除。

## 返回值

被删除了个元素/列/行的向量、矩阵或表。

## 例子

```dolphindb
x=1..10;
x.drop(2);
// output
[3,4,5,6,7,8,9,10]
x.drop(-2);
// output
[1,2,3,4,5,6,7,8]

x=1..10$2:5;
x;
```

| #0 | #1 | #2 | #3 | #4 |
| --- | --- | --- | --- | --- |
| 1 | 3 | 5 | 7 | 9 |
| 2 | 4 | 6 | 8 | 10 |

```dolphindb
drop(x,2);
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 5 | 7 | 9 |
| 6 | 8 | 10 |

```dolphindb
x drop -2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 5 |
| 2 | 4 | 6 |

```dolphindb
t=table(1 2 3 4 as x, 11..14 as y);
t;
```

| x | y |
| --- | --- |
| 1 | 11 |
| 2 | 12 |
| 3 | 13 |
| 4 | 14 |

```dolphindb
t.drop(2);
```

| x | y |
| --- | --- |
| 3 | 13 |
| 4 | 14 |

**相关函数：**[pop!](../p/pop_.html)、[removeHead!](../r/removeHead_.html)、[removeTail!](../r/removeTail_.html)、[remove!](../r/remove.html)
