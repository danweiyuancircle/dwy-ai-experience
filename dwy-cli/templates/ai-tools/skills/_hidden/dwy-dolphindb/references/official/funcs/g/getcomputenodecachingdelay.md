---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getcomputenodecachingdelay.html
fetched_at: 2026-05-19T09:23:15Z
category: funcs
title: getComputeNodeCachingDelay
sha1: b4fc9d2a9714b3db5c7fff422c149e3e4b433892
---

# getComputeNodeCachingDelay

## 语法

`getComputeNodeCachingDelay()`

## 详情

查看当前节点下配置项 *computeNodeCachingDelay* 的生效值，单位为秒。

## 参数

无

## 详情

整型标量。

## 例子

```dolphindb
getComputeNodeCachingDelay() 

// output: 580
```

相关函数：[setComputeNodeCachingDelay](../s/setcomputenodecachingdelay.html)
