---
source_url: https://docs.dolphindb.cn/zh/funcs/ho_funcs/call.html
fetched_at: 2026-05-19T09:44:50Z
category: funcs
title: call
sha1: acbe3354562a6e07d7c2eb88e7bcf9117a952e0b
---

# call

## 语法

`call(func, args...)`

## 详情

用指定的参数调用一个函数。常常用在 [each](each.html)/[peach](peach.html) 或 [loop](loop.html)/[ploop](ploop.html) 中，用来调用一批函数。

## 参数

- **func** 是一个函数名。
- **args** 是函数func的参数。

## 返回值

取决于 `func(args)` 的返回值。

## 例子

```dolphindb
call(sum, 1..10);
// output
55
// 等同于sum(1..10)

each(call, [avg, sum], [0..10, 0..100]);
// output
[5,5050]

each(call{, 1..3},(sin,log));
// 注意call{, 1..3}是一个部分应用
```

| sin | log |
| --- | --- |
| 0.841471 | 0 |
| 0.909297 | 0.693147 |
| 0.14112 | 1.098612 |

**相关函数：**[nothrowCall](nothrowcall.html)
