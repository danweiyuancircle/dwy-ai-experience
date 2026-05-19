---
source_url: https://docs.dolphindb.cn/zh/funcs/m/max.html
fetched_at: 2026-05-19T09:31:13Z
category: funcs
title: max
sha1: 8ed7e126cfb3d27a629dacb6f84e21a79eb51ad7
---

# max

## 语法

`max(X, [Y])`

## 详情

返回输入数据中的最大值。

支持以下两种调用方式：

- 仅输入一个参数 *X*，用于计算 *X* 的最大值。比较时忽略 NULL 值。
- 输入两个参数，用于按元素比较两个数据对象，返回较大值。比较时不忽略 NULL 值。

请注意，从 2.00.8 版本开始，`max`
处理时间类型数据的行为（之前版本统一转换为长整型）修改为：

- 若 *X* 和 *Y*
  是时间类型标量，系统会将时间类型统一为两者中较高精度对应的类型，再比较大小。
- 若 *X* 或 *Y* 是向量、矩阵或表，则必须具有相同的时间类型。

DolphinDB、NumPy 与 Python 内置的 max 函数虽均用于返回最大值，但存在以下差异：

- DolphinDB 支持标量、向量、矩阵、表及时间类型；NumPy 支持多维数组；Python 内置支持任意可迭代对象。
- DolphinDB 支持双参数调用；Python 内置支持多参数比较；NumPy 不支持多参数比较。
- Python 内置 max 函数支持指定 *key* 自定义排序规则。

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
  `max(X[i], Y)`。
- 若 *Y* 和 *X* 类型和长度一致，返回对应位置较大值组成的对象。

## 例子

```dolphindb
max(1 2 3);
// output: 3

max(7.8 9 5.4);
// output: 9

(5 8 2 7).max();
// output: 8

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |

```dolphindb
max(m);
// output: [3,6]
```

```dolphindb
max(1 2 3, 2)
// output: 2 2 3

n = matrix(1 1 1, 5 5 5)
n;
```

| #0 | #1 |
| --- | --- |
| 1 | 5 |
| 1 | 5 |
| 1 | 5 |

```dolphindb
max(m, n);
```

| #0 | #1 |
| --- | --- |
| 1 | 5 |
| 2 | 5 |
| 3 | 6 |

`max` 可以搭配 select 使用, 返回某列的最大值：

```dolphindb
t = table(`abb`aac`aaa as sym, 1.8 2.3 3.7 as price);
select max price from t;
```

| max\_price |
| --- |
| 3.7 |

max 可以应用于字符串，返回字典序最大的字符串：

```dolphindb
select max sym from t;
```

| max\_sym |
| --- |
| abb |

相关函数：[mmax](mmax.html)
