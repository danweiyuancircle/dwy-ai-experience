---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lowDouble.html
fetched_at: 2026-05-19T09:30:29Z
category: funcs
title: lowDouble
sha1: f4d36bbe9113b355038c8bfbd29f685f54e9eabf
---

# lowDouble

## 语法

`lowDouble(X)`

## 详情

返回值为 *X* 的低位8字节的数据，为 DOUBLE 类型。

## 参数

**X** 是一个标量或向量，必须是16字节的数据类型。

## 例子

```dolphindb
x=1 2 3 4
y=4 3 2 1
points = point(x, y)
x1 = lowDouble(points)
```

输出返回：[1,2,3,4]

获取一个复数的实部（实数）：

```dolphindb
a=complex(2, 5)
lowDouble(a)
```

输出返回：2
