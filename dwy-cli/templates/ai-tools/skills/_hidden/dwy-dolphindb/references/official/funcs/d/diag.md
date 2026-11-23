---
source_url: https://docs.dolphindb.cn/zh/funcs/d/diag.html
fetched_at: 2026-05-19T09:18:53Z
category: funcs
title: diag
sha1: 202f46c00d74a39d99b452602f6ca2fa6cab4a78
---

# diag

## 语法

`diag(X)`

## 详情

处理矩阵的对角线元素，支持以下两种转换：

- 向量转对角矩阵：将向量作为主对角线元素构造对角矩阵。
- 方阵提取对角线：从方阵中提取主对角线元素。

DolphinDB 的 `diag` 函数和 `numpy.diag`
函数在基本功能上相似，但在参数设计、功能范围、空值处理上存在区别。

- DolphinDB `diag` 函数仅支持一个参数，不支持对角线偏移、仅能处理主对角线、输入必须是向量或方阵
- `numpy.diag` 函数支持可选偏移参数、可以提取/设置任意对角线，输入为一维或二维数组。
- 在空值处理方面，DolphinDB `diag` 函数将 NULL 视为 0，而
  `numpy.diag` 对 NaN/Inf 采取原样保留策略。

## 参数

**X** 是一个向量或方阵。

## 返回值

- 如果 *X* 是向量，返回一个矩阵。
- 如果 *X* 是方阵，返回一个向量。

## 例子

```dolphindb
diag(1..5);
```

| #0 | #1 | #2 | #3 | #4 |
| --- | --- | --- | --- | --- |
| 1 | 0 | 0 | 0 | 0 |
| 0 | 2 | 0 | 0 | 0 |
| 0 | 0 | 3 | 0 | 0 |
| 0 | 0 | 0 | 4 | 0 |
| 0 | 0 | 0 | 0 | 5 |

```dolphindb
m=1..4$2:2;
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 3 |
| 2 | 4 |

```dolphindb
diag(m);

// output: [1,4]
```
