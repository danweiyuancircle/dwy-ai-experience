---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getMemoryStat.html
fetched_at: 2026-05-19T09:25:02Z
category: funcs
title: getMemoryStat
sha1: 04311c100c6a62781cbaa6a462e2082008192664
---

# getMemoryStat

## 语法

`getMemoryStat()`

## 详情

获取当前节点已分配的内存和未使用的内存。两者之差为已占用内存。

## 参数

无

## 返回值

返回一个字典，其 key 值的含义为：

- allocatedBytes：当前节点已分配的内存，单位为字节。
- freeBytes：当前节点已分配但未使用的内存，单位为字节。

## 例子

```dolphindb
getMemoryStat();

// output
freeBytes->6430128
allocatedBytes->35463168
```
