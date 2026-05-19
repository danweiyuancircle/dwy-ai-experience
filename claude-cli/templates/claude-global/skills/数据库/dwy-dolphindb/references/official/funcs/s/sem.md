---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sem.html
fetched_at: 2026-05-19T09:38:13Z
category: funcs
title: sem
sha1: 0bb003f6cecbc0c232fdcb190caadf3b2ec06541
---

# sem

## 语法

`sem(X)`

## 详情

返回 *X* 的平均值的标准误差。

若 *X* 为矩阵，计算每列的标准误差，返回一个向量。

若 *X* 为表，计算每列的标准误差，返回一个表。

注：

DolphinDB `sem` 与 [scipy.stats.sem](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.sem.html) 的核心功能相同。区别在于：

- DolphinDB `sem` 支持数值型向量、矩阵或表，矩阵和表按列计算，并忽略 NULL。
- `scipy.stats.sem` 支持数组的轴向计算，默认遇到 NaN 会返回 NaN，可设置*nan\_policy*="omit" 忽略 NaN。
- 若输入数据和缺失值处理方式一致，二者的返回结果一致。

## 参数

**X** 是数值型向量、矩阵或表。

## 返回值

返回 DOUBLE 类型的标量、向量或表。

## 例子

```dolphindb
sem([85,90,95,NULL]);
// output
2.886751
```
