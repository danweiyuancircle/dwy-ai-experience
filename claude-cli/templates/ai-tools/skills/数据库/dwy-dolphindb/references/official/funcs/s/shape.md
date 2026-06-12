---
source_url: https://docs.dolphindb.cn/zh/funcs/s/shape.html
fetched_at: 2026-05-19T09:39:13Z
category: funcs
title: shape
sha1: fb66b1157c93456028cfddbd9570c5727963fd9b
---

# shape

## 语法

`shape(X)`

## 详情

以数据对的形式返回标量、向量或矩阵的维度。

注：

DolphinDB `shape` 与 [numpy.shape](https://numpy.org/doc/stable/reference/generated/numpy.shape.html) 的核心功能相同。区别在于：

- DolphinDB `shape`
  返回数据对，以`行数:列数`的形式描述对象，标量返回1:1，向量返回`长度:1`，矩阵和表返回`行数:列数`。
- `numpy.shape`
  返回元组，表示数组各维度的长度，标量返回`()`，一维数组返回`(n,)`，二维数组返回`(m,
  n)`。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

INT PAIR 类型标量。

## 例子

标量的维度总是 1:1

```dolphindb
shape 1;
// output
1:1

s;
```

向量的维度总是向量长度:1

```dolphindb
shape 1 5 3 7 8;
// output
5:1
```

矩阵的维度

```dolphindb
m=(5 3 1 4 9 10)$3:2;
m;
```

| #0 | #1 |
| --- | --- |
| 5 | 4 |
| 3 | 9 |
| 1 | 10 |

```dolphindb
shape m;

// output
3 :2
```

表的维度

```dolphindb
t=table(1 2 3 as x, 4 5 6 as y);
t;
```

| x | y |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
shape t;
// output
3 :2
```
