---
source_url: https://docs.dolphindb.cn/zh/funcs/m/min.html
fetched_at: 2026-05-19T09:31:53Z
category: funcs
title: min
sha1: 176a3cad964385311e6d0afb88218b853275c661
---

# min

## 语法

`min(X, [Y])`

## 详情

返回输入数据中的最小值。

支持以下两种调用方式：

- 仅输入一个参数 *X*，用于计算 *X* 的最小值。比较时忽略 NULL 值。
- 输入两个参数，用于按元素比较两个数据对象，返回较小值。比较时不忽略 NULL 值。

请注意，从 2.00.8 版本开始，min 处理时间类型数据的行为（之前版本统一转换为长整型）修改为：

- 若 *X* 和 *Y*
  是时间类型标量，系统会将时间类型统一为两者中较高精度对应的类型，再比较大小。
- 若 *X* 或 *Y* 是向量、矩阵或表，则必须具有相同的时间类型。

DolphinDB `min` 函数和 `numpy.min`
函数的功能一样，区别在于计算方式和空值处理不同：

- DolphinDB 支持双参数，可以逐元素比较；而 Numpy 不支持双参数。
- 当 DolphinDB `min` 输入单参数时，对于矩阵/表按列计算最小值，按行计算需要使用
  `rowMin` 函数；而 Numpy 则可以通过 *axis* 参数控制计算轴。
- DolphinDB 单参数时忽略 NULL 值，双参数时 NULL 值参与比较；Numpy 默认不忽略 NaN 值。

## 参数

**X** 可以是标量、向量、矩阵或表。

**Y** 为可选参数，可以是标量或者是和 *X* 长度相同的向量或者矩阵。

## 返回值

**单参数调用：**

- 若 *X* 是向量，返回一个标量。
- 若 *X* 为矩阵，返回一个向量。
- 若 *X* 为表，返回一个表。

**双参数调用：**

- 若 *Y* 是标量，返回与 *X* 维度相同的对象，每个元素为
  `min(X[i], Y)`。
- 若 *Y* 和 *X* 类型和长度一致，返回对应位置较小值组成的对象。

## 例子

```dolphindb
min(1 2 3);
// output
1;

min(2.0 1.1 0.1 NULL);
// output
0.1

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
min(m);
// output
[1,4]
```

```dolphindb
min(1 2 3, 2)
// output
1 2 2

n = matrix(1 1 1, 5 5 5)
n;
```

| #0 | #1 |
| --- | --- |
| 1 | 5 |
| 1 | 5 |
| 1 | 5 |

```dolphindb
min(m, n);
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 1 | 5 |
| 1 | 5 |

`min` 可以搭配 select 使用, 返回某列的最小值：

```dolphindb
t = table(`abb`aac`aaa as sym, 1.8 2.3 3.7 as price);
select min price from t;
```

| min\_price |
| --- |
| 1.8 |

`min` 可以应用于字符串，返回字典序最小的字符串：

```dolphindb
select min sym from t;
```

| min\_sym |
| --- |
| aaa |

相关函数：[mmin](mmin.html)
