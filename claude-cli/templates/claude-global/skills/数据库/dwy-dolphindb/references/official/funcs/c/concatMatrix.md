---
source_url: https://docs.dolphindb.cn/zh/funcs/c/concatMatrix.html
fetched_at: 2026-05-19T09:15:40Z
category: funcs
title: concatMatrix
sha1: 22215f19b4f8f00d9d0bef30527c225dd7daec17
---

# concatMatrix

## 语法

`concatMatrix(X, [horizontal=true])`

## 详情

水平或垂直拼接多个矩阵。

如果水平拼接多个矩阵，它们的行数必须相同；如果垂直拼接多个矩阵，它们的列数必须相同。

## 参数

**X** 由多个矩阵构成的元组。

**horizontal** 布尔值，是否水平拼接矩阵，默认值为 true。若为 false 表示垂直拼接。

## 返回值

返回一个拼接后的矩阵对象。

## 例子

```dolphindb
m1 = matrix(4 0 5, 2 1 8);
m2 = matrix(2 9 8, 3 7 -3, 6 4 2, 0 5 8);
m3 = matrix(1 -1 6 2, 1 -3 1 9, 5 3 0 -4, 1 NULL 3 4);
concatMatrix([m1, m2]);
```

| col1 | col2 | col3 | col4 | col5 | col6 |
| --- | --- | --- | --- | --- | --- |
| 4 | 2 | 2 | 3 | 6 | 0 |
| 0 | 1 | 9 | 7 | 4 | 5 |
| 5 | 8 | 8 | -3 | 2 | 8 |

```dolphindb
print concatMatrix([m2, m3], false);
```

| col1 | col2 | col3 | col4 |
| --- | --- | --- | --- |
| 2 | 3 | 6 | 0 |
| 9 | 7 | 4 | 5 |
| 8 | -3 | 2 | 8 |
| 1 | 1 | 5 | 1 |
| -1 | -3 | 3 |  |
| 6 | 1 | 0 | 3 |
| 2 | 9 | 4 | 4 |
