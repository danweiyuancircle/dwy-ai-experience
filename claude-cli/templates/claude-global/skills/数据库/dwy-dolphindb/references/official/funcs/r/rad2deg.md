---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rad2deg.html
fetched_at: 2026-05-19T09:34:51Z
category: funcs
title: rad2deg
sha1: db363fb33cca0bd53f81f7a870afb663fa275f10
---

# rad2deg

## 语法

`rad2deg(X)`

## 详情

将 *X* 的角单位从弧度转换为度。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

数据类型是 DOUBLE，数据形式与 *X* 相同。

## 例子

```dolphindb
rad2deg(pi);
// output
180
```

相关函数：[deg2rad](../d/deg2rad.html)
