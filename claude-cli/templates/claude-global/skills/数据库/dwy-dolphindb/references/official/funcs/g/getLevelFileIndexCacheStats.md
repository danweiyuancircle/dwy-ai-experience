---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getLevelFileIndexCacheStats.html
fetched_at: 2026-05-19T09:24:50Z
category: funcs
title: getLevelFileIndexCacheStatus
sha1: 4b1ff41b7d1db2b2bd70ce4fff0edabe4444a19e
---

# getLevelFileIndexCacheStatus

## 语法

`getLevelFileIndexCacheStatus()`

## 详情

获取所有 level file 的索引内存占用的情况。

## 参数

无

## 返回值

返回一个字典，包含以下 key 值：

- capacity：level file 索引内存占用上限；
- usage：level file 索引使用的内存，单位为字节。

## 例子

```dolphindb
getLevelFileIndexCacheStatus()

// output
usage->0
capacity->429496729
```
