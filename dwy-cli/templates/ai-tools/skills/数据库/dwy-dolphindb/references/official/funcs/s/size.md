---
source_url: https://docs.dolphindb.cn/zh/funcs/s/size.html
fetched_at: 2026-05-19T09:39:25Z
category: funcs
title: size
sha1: 3c7b33badbc8ce0af27384aef9f9aa0ca4fa062a
---

# size

## 语法

`size(X)`

## 详情

对于向量或矩阵，`size` 返回元素的个数，而 [count](../c/count.html) 返回的是非 NULL 元素个数。

对于内存表，`size` 返回行数。

注：

DolphinDB 的 `size`
函数用于返回输入对象的元素总量：针对向量或矩阵，返回其包含的元素总个数；针对内存表，返回其行数。NumPy 的 `size`
函数用于返回数组沿指定轴方向的元素数量：在未指定 `axis` 参数时，返回数组所有维度上的元素总数；在指定
`axis` 参数时，返回该特定维度上的元素个数。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

INT 类型标量。

## 例子

```dolphindb
size(3 NULL 5 6);
// output
4
count(3 NULL 5 6);
// output
3

m=1 2 3 NULL 4 5$2:3;
m;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 4 |
| 2 |  | 5 |

```dolphindb
size(m);
// output
6

count(m);
// output
5

t = table(1 NULL 3 as id, 3 NULL 9 as qty);
t;
```

| id | qty |
| --- | --- |
| 1 | 3 |
|  |  |
| 3 | 9 |

```dolphindb
size(t);
// output
3

count(t);
// output
3
```
