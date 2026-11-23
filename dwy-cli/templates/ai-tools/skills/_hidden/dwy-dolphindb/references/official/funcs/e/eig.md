---
source_url: https://docs.dolphindb.cn/zh/funcs/e/eig.html
fetched_at: 2026-05-19T09:20:32Z
category: funcs
title: eig
sha1: e4f48e91f522d33bdef4f71f4b0f84bd2ccee7bc
---

# eig

## 语法

`eig(A)`

## 详情

计算矩阵的特征值与特征向量。

注：

- DolphinDB `eig` 与 [numpy.linalg.eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html) 功能相同。
- [numpy.linalg.eig](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html) 和 [scipy.linalg.eig](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eig.html)
  是通用的特征分解函数，其适用范围更广，并非专门针对实对称矩阵或 Hermitian 矩阵设计。

## 参数

**A** 是一个实对称矩阵或 Hermitian（共轭对称）矩阵。

## 返回值

返回一个字典，为矩阵 *A* 的特征值（values）与特征向量（vectors）。

## 例子

```dolphindb
A = 1 1 2 7 9 3 5 7 0 $ 3:3;
eig(A);
// output
vectors->
#0        #1       #2
--------- -------- ---------
0.839752  0.169451 -0.515852
-0.301349 0.935753 -0.18318
0.45167   0.309277 0.836864

values->[1.716868,10.17262,-1.889488]
```

对应第一个特征值 1.716868 的特征向量为：

```dolphindb
eig(A).vectors[0];
// output
[0.839752,-0.301349,0.45167]
```

使用 `numpy.linalg.eigh` 函数计算同一个矩阵的特征值与特征向量。返回的特征值顺序可能与 DolphinDB
`eig` 不同，特征向量符号也可能相反，但在数学意义上等价。

```dolphindb
import numpy as np

A = np.array([[1., 7., 5.],
              [1., 9., 7.],
              [2., 3., 0.]])

w, v = np.linalg.eigh(A)

print("values:")
print(w)

print("vectors:")
print(v)

""" 输出：
values:
[-1.88948817  1.71686814 10.17262003]
vectors:
[[-0.51585193  0.83975187 -0.16945081]
 [-0.18318039 -0.30134864 -0.93575314]
 [ 0.83686422  0.45167    -0.30927736]]
"""
```
