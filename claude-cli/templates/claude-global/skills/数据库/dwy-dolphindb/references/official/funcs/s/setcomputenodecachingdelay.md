---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setcomputenodecachingdelay.html
fetched_at: 2026-05-19T09:38:28Z
category: funcs
title: setComputeNodeCachingDelay
sha1: a58e5709228b39d4bacf4c035bd1d3b0b259b4ea
---

# setComputeNodeCachingDelay

## 语法

`setComputeNodeCachingDelay(delay)`

## 详情

在线设置当前节点下配置项 *computeNodeCachingDelay* 的生效值。只能由管理员在控制节点执行。

## 参数

**delay** 非负整数，表示时间间隔，单位为秒。

## 例子

```dolphindb
setComputeNodeCachingDelay(580)
```

相关函数：[getComputeNodeCachingDelay](../g/getcomputenodecachingdelay.html)
