---
source_url: https://docs.dolphindb.cn/zh/funcs/ho_funcs/pcall.html
fetched_at: 2026-05-19T09:45:07Z
category: funcs
title: pcall
sha1: c5af6aea82caf67866cf082c37af12bb3c1ecaf1
---

# pcall

## 语法

`pcall(func, args...)`

## 详情

将输入参数分成几个部分，并行计算，最后将结果合并。如果输入参数的长度小于100,000，*pcall*
函数不会并行计算。

## 参数

- **func** 是一个函数。该函数的输出结果可以是一个向量或表，并且它们的长度必须与输入参数args的长度相同。
- **args** 是func的参数。它可以是表、向量或元组。输入参数中的所有向量或表列必须长度相同。

## 返回值

向量或表，取决于 *func* 的输出结果。

## 例子

```dolphindb
x = rand(1.0, 10000000);
timer(10) sin(x);
```

输出返回：

Time elapsed: 739.561 ms

```dolphindb
timer(10) pcall(sin, x);
```

输出返回：

Time elapsed: 404.56 ms
