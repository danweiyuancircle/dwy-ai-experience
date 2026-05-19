---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isControllerInitialized.html
fetched_at: 2026-05-19T09:28:23Z
category: funcs
title: isControllerInitialized
sha1: 99134303a3e0f87311b24d014658e9ad75c01e19
---

# isControllerInitialized

## 语法

`isControllerInitialized()`

## 详情

查看控制节点是否启动完成。若启动完成返回 true，否则返回 false。普通集群环境下，仅在控制节点调用；高可用集群环境下，仅在
leader 节点调用。

## 返回值

布尔标量。

## 例子

```dolphindb
isControllerInitialized()
// output: true
```

相关函数：[isDataNodeInitialized](isDataNodeInitialized.html)
