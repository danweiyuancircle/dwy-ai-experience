---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setprefetchcomputenodedata.html
fetched_at: 2026-05-19T09:38:57Z
category: funcs
title: setPrefetchComputeNodeData
sha1: 95232075b189fa9dfcf819458a4bea600ceea0ad
---

# setPrefetchComputeNodeData

## 语法

`setPrefetchComputeNodeData(flag)`

## 详情

在线设置当前节点下配置项 *enableComputeNodePrefetchData* 的生效值。只能由管理员在控制节点执行。

## 参数

**flag** 布尔值，表示配置项 *enableComputeNodePrefetchData* 的内存生效值。

## 例子

```dolphindb
setPrefetchComputeNodeData(false)
```

相关函数：[getPrefetchComputeNodeData](../g/getprefetchcomputenodedata.html)
