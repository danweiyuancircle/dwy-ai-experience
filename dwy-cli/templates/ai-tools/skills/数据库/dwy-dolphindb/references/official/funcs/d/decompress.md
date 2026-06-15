---
source_url: https://docs.dolphindb.cn/zh/funcs/d/decompress.html
fetched_at: 2026-05-19T09:18:27Z
category: funcs
title: decompress
sha1: 3092eded8a006750332ead379874f509e895549e
---

# decompress

## 语法

`decompress(X)`

## 详情

对一个压缩后的向量进行解压缩。

## 参数

**X** 是一个压缩后的向量。

## 返回值

返回一个向量。

## 例子

```dolphindb
x=1..100000000
y=compress(x, "delta");

y.typestr();
// output: HUGE COMPRESSED VECTOR

z=decompress(y);
z.size();
// output: 100000000
```

相关函数：[compress](../c/compress.html)
