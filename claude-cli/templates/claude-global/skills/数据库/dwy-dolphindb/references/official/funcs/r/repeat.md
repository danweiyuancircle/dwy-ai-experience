---
source_url: https://docs.dolphindb.cn/zh/funcs/r/repeat.html
fetched_at: 2026-05-19T09:35:58Z
category: funcs
title: repeat
sha1: 3380c69f4de52ce03995d2aea09bc4a3ce6885c7
---

# repeat

## 语法

`repeat(X, n)`

## 详情

将 *X* 重复 *n* 次。

DolphinDB 的 `repeat` 和 NumPy 的 `numpy.repeat`
存在以下区别：

- 支持的数据类型不同：DolphinDB 的 `repeat` 仅支持字符串标量或字符串向量，而
  `numpy.repeat` 可用于数值、布尔等多种 ndarray 数据类型。
- 语义不同：
  - DolphinDB 的 `repeat` 对每个字符串元素进行内容级重复，，是字符串级变换；而 NumPy
    的 `numpy.repeat`
    是“逐元素复制数组元素”，，是数组元素级展开。前者改变元素内容，后者改变元素数量。例如：DolphinDB
    `repeat(["ab", "cd"], 2)` 输出
    `["abab","cdcd"]`；`np.repeat(["ab","cd"],
    2)` 输出 `['ab' 'ab' 'cd' 'cd']`。
  - NumPy 支持按元素指定不同重复次数（vectorized repetition），例如：Numpy 支持
    `np.repeat(["a","b","c"], [1,2,3])`；而
    DolphinDB 不支持对应语义。
- 返回值类型不同：DolphinDB 返回 STRING 标量或向量，而 NumPy 返回 ndarray。

## 参数

**X** 是一个字符串或字符串向量。

**n** 是一个非负整数，表示重复的次数。

## 返回值

返回一个字符串或字符串向量。

## 例子

```dolphindb
repeat(`FB, 3);
// output: FBFBFB
repeat(`AB`CD,2);
// output: ["ABAB","CDCD"]
```
