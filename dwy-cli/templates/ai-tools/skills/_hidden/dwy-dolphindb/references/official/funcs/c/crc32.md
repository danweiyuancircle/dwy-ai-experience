---
source_url: https://docs.dolphindb.cn/zh/funcs/c/crc32.html
fetched_at: 2026-05-19T09:16:09Z
category: funcs
title: crc32
sha1: 6116df5b89586bf96c039d053f6a59b1fbd3c234
---

# crc32

## 语法

`crc32(str, [cksum=0])`

## 详情

根据 CRC32 算法，对字符串进行哈希，生成 INT 类型数据。

## 参数

**str** 是一个字符串标量、向量或表。

**cksum** 是整型标量或向量。

## 返回值

INT 类型标量/向量/表。

## 例子

```dolphindb
a=crc32(`aa`cc,1);
a;
// output
[512829590,-1029100744]

typestr(a);
// output
FAST INT VECTOR
```
