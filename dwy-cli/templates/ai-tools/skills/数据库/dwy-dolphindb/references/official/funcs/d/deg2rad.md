---
source_url: https://docs.dolphindb.cn/zh/funcs/d/deg2rad.html
fetched_at: 2026-05-19T09:18:32Z
category: funcs
title: deg2rad
sha1: 0ae3ed23216fcb6ca5a6b55e4a557e96dec17946
---

# deg2rad

## 语法

`deg2rad(X)`

## 详情

将角的单位从度转换成弧度。

注：

与 NumPy 的 [numpy.deg2rad](https://numpy.com.cn/doc/stable/reference/generated/numpy.deg2rad.html) 功能基本相同，区别在于 DolphinDB 的
`deg2rad` 只接受一个参数 *X*，不支持 `numpy.deg2rad`
中的 *out*、*where*、*casting*、*order* 等参数。

## 参数

**X** 可以是标量、向量、矩阵或表。

## 返回值

返回值类型与 *X* 保持一致，表示对应弧度值。

## 例子

```dolphindb
deg2rad 45 90 180 360;
// output
[0.785398,1.570796,3.141593,6.283185]
```

相关函数：[rad2deg](../r/rad2deg.html)
