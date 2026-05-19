---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getcomputenodecachestat.html
fetched_at: 2026-05-19T09:23:13Z
category: funcs
title: getComputeNodeCacheStat
sha1: d1c12d445adf420ed12dab35ffc7633873eaebc2
---

# getComputeNodeCacheStat

## 语法

`getComputeNodeCacheStat()`

## 详情

应用于计算组中的计算节点上，返回该节点的二级缓存信息。

## 参数

无

## 返回值

返回一个表，包含以下列：

- memCacheUsage：内存缓存的使用量，单位为 MB。
- memCacheSize：内存缓存的最大容量，单位为 MB。
- diskCacheUsage：磁盘缓存的使用量，单位为 MB。
- diskCacheSize：磁盘缓存的最大容量，单位为 MB。

## 例子

```dolphindb
getComputeNodeCacheStat()
```

| memCacheUsage | memCacheSize | diskCacheUsage | diskCacheSize |
| --- | --- | --- | --- |
| 114.51725769042969 | 1,024 | 0 | 65,536 |
