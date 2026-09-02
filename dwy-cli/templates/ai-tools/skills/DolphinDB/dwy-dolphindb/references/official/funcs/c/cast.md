---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cast.html
fetched_at: 2026-05-19T09:14:33Z
category: funcs
title: cast
sha1: b08ce21ac132ccbd2e5992279fe92b3321ef415b
---

# cast

## 语法

`cast(X, Y)` 或 `X $ Y`

## 详情

- 把一个数据类型转换成另一个
- 改变一个矩阵的形状
- 将向量转换成矩阵

## 参数

**X** 可以是任意数据形式。

**Y** 是数据类型或数据对。

## 返回值

取决于 *Y* 的数据类型与形式。

## 例子

```dolphindb
x=8.9$INT;
x;
```

返回：9

```dolphindb
x=1..10;
x;
```

返回：[1,2,3,4,5,6,7,8,9,10]

```dolphindb
typestr x;
```

返回：FAST INT VECTOR

```dolphindb
x/2;
```

返回：[0,1,1,2,2,3,3,4,4,5]

```dolphindb
x=x$DOUBLE;
typestr x;
```

返回：FAST DOUBLE VECTOR

```dolphindb
x/2;
```

返回：[0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]

```dolphindb
x=`IBM`MS;
typestr x;
```

返回：STRING VECTOR

```dolphindb
x=x$SYMBOL;
typestr x;
```

返回：FAST SYMBOL VECTOR

```dolphindb
x=`128.9;
typestr x;
```

返回：STRING

```dolphindb
x=x$INT;
x;
```

返回：128

```dolphindb
typestr x;
```

返回：INT

以下这个例子将向量转换为矩阵：

```dolphindb
m=1..8$2:4;
m;
```

得到：

| 0 | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 3 | 5 | 7 |
| 2 | 4 | 6 | 8 |

以下例子改变一个矩阵的形状：

```dolphindb
m$4:2;
```

得到：

| 0 | 1 |
| --- | --- |
| 1 | 5 |
| 2 | 6 |
| 3 | 7 |
| 4 | 8 |

```dolphindb
m$1:size(m);
```

得到：

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
