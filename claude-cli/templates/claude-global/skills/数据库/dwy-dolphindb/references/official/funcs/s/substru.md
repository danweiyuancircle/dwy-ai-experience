---
source_url: https://docs.dolphindb.cn/zh/funcs/s/substru.html
fetched_at: 2026-05-19T09:40:58Z
category: funcs
title: substru
sha1: 8a7c7fe62303d835ff452e8442617e8423cb8284
---

# substru

## 语法

`substru(X, offset, [length])`

## 详情

从 *X* 的指定位置开始截取指定长度的字符串。*X* 的第一个字符的位置为0。 如果 *length* 超过了 *X*
的长度，则到 *X* 的尾部结束。

## 参数

**X** 是 Unicode 编码的字符串。它可以是标量或向量。

**offset** 是一个非负整数。

**length** 是一个正整数。

## 返回值

STRING 类型标量或向量。

## 例子

```dolphindb
substru("这是测试字符串",0,4)
// output
这是测试

substru("这是测试字符串",4,3)
// output
字符

substru("这是测试字符串",2)
// output
测试字符串

substru("这是测试字符串",2,10)
// output
测试字符串
```

相关函数：[substr](substr.html)
