---
source_url: https://docs.dolphindb.cn/zh/funcs/m/md5.html
fetched_at: 2026-05-19T09:31:27Z
category: funcs
title: md5
sha1: 98b03a913926eec56746c4e54b6ea264cb5fb46e
---

# md5

## 语法

`md5(X)`

## 详情

根据 MD5 算法，对字符串进行哈希，生成 INT128 类型的数据。

## 参数

**X** 是一个字符串标量或向量。

## 返回值

INT128 类型标量或向量。

## 例子

```dolphindb
a=md5(`e`f);
a;
// output: [e1671797c52e15f763380b45e841ec32,8fa14cdd754f91cc6554c9e71929cce7]

typestr(a);
// output: INT128
```
