---
source_url: https://docs.dolphindb.cn/zh/funcs/d/det.html
fetched_at: 2026-05-19T09:18:52Z
category: funcs
title: det
sha1: a4dc23f079340fc408a14d24d2b0a436aa6d23ca
---

# det

## 语法

`det(X)`

## 详情

返回矩阵 *X* 的行列式（determinant）。在计算中，NULL 值用 0 代替。

DolphinDB `det` 和 `numpy.linalg.det`
的核心功能相同，在参数设计、空值处理上存在差异：

- DolphinDB `det` 要求入参必须是矩阵对象；`numpy.linalg.det`
  接受类数组对象并自动转换为 ndarray。
- 在缺失值处理上，DolphinDB `det` 将 NULL 视为
  0；`numpy.linalg.det` 包含 NaN/Inf 时会返回 NaN/Inf。详见下文例子。

## 参数

**X** 是一个矩阵。

## 返回值

DOUBLE 类型标量。

## 例子

```dolphindb
x=1..4$2:2;
x;
```

| #0 | #1 |
| --- | --- |
| 1 | 3 |
| 2 | 4 |

```dolphindb
x.det();
// output: -2

x=1 2 3 6 5 4 8 7 0$3:3;
x;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 6 | 8 |
| 2 | 5 | 7 |
| 3 | 4 | 0 |

```dolphindb
det(x);
// output: 42

x=1 2 3 6 5 4 8 7 NULL $3:3;
x;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 6 | 8 |
| 2 | 5 | 7 |
| 3 | 4 |  |

```dolphindb
det(x);
// output: 42
```

以下代码在 Python 中运行。代码展示了 `numpy.linalg.det` 对 NaN/Inf
的处理逻辑。

```dolphindb
import numpy as np

A = np.array([
    [1, 6, 8],
    [2, 5, 7],
    [3, 4, np.nan]
])

print(np.isnan(np.linalg.det(A)))
# 返回 True

B = np.array([
    [1, 6, 8],
    [2, 5, 7],
    [3, 4, np.inf]
])
print(np.isnan(np.linalg.det(B)))

# 返回 True
```
