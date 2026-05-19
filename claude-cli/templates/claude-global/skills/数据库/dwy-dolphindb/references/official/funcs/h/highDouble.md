---
source_url: https://docs.dolphindb.cn/zh/funcs/h/highDouble.html
fetched_at: 2026-05-19T09:27:16Z
category: funcs
title: highDouble
sha1: 29b548e2d9093897737bc5dc1267669beae99f29
---

# highDouble

## 语法

`highDouble(X)`

## 详情

返回 *X* 的高位 8 字节的数据，为 DOUBLE 类型。

## 参数

**X** 是一个标量或向量，必须是 16 字节的数据类型。

## 例子

```dolphindb
x=1 2 3 4
y=4 3 2 1
points = point(x, y)
x1 = highDouble(points)
// output
[4,3,2,1]
```

获取一个复数的虚部（虚数）

```dolphindb
a=complex(2, 5)
highDouble(a)
// output
5
```
