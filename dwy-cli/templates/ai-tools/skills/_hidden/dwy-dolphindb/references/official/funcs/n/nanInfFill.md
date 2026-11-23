---
source_url: https://docs.dolphindb.cn/zh/funcs/n/nanInfFill.html
fetched_at: 2026-05-19T09:33:05Z
category: funcs
title: nanInfFill
sha1: fb723ecf84bd7cca4bc62af2ff8097ec914fe3c2
---

# nanInfFill

## 语法

`nanInfFill(X,Y)`

## 详情

在 DolphinDB 中，浮点数中出现的 NaN 和 Inf
值自动替换为空值。而在外部数据导入或计算过程中，可能出现极端场景，导致上述两个特殊值的引入。该函数用于替换这两个特殊值。

可使用指定 *Y* 值对 *X* 中存在的 NaN 或 Inf 值进行替换。

注：

当 *X* 为字典时，该函数仅对 value 值进行替换。

## 参数

**X** 是除集合外任一数据形式的浮点数。

**Y** 是一个浮点数。

## 返回值

返回浮点型，数据形式同 *X*。

## 例子

```dolphindb
x = [float(`inf), 2, 3, float(`nan), 5, 6, 7]
nanInfFill (x, 2.2)
x = matrix(1..3, [float(`inf), float(`nan), 1.0])
nanInfFill(x, 1.2)
```

相关函数：[isNanInf](../i/isNanInf.html), [countNanInf](../c/countNanInf.html)
