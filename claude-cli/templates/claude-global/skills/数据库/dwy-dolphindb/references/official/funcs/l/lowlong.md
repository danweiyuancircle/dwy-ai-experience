---
source_url: https://docs.dolphindb.cn/zh/funcs/l/lowlong.html
fetched_at: 2026-05-19T09:30:32Z
category: funcs
title: lowLong
sha1: 441a743e054fcecfb2af242c8c530bef431d1a7f
---

# lowLong

## 语法

`lowLong(X)`

## 详情

返回值为 *X* 的低位8字节的数据，为 LONG 类型。

## 参数

**X** 是一个标量、向量、表、数据对或者字典，且必须为16字节的数据类型（支持 UUID、IPADDR、INT128、COMPLEX、POINT）。

## 例子

```dolphindb
x =ipaddr("192.168.1.13")
x1 = lowLong(x)
print(x1)
//output: 3232235789
```

```dolphindb
x=1 2 3 4
y=4 3 2 1
points = point(x, y)
x1 = lowLong(points)
//output: [4607182418800017408,4611686018427387904,4613937818241073152,4616189618054758400]
```
