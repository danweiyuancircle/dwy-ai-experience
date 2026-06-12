---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isDataNodeInitialized.html
fetched_at: 2026-05-19T09:28:25Z
category: funcs
title: isDataNodeInitialized
sha1: 1c0d38d65735ef03c0e425ca6cb901a12188441a
---

# isDataNodeInitialized

## 语法

`isDataNodeInitialized()`

## 详情

查看当前节点是否启动完成。若启动完成返回true，否则返回false。

只适用于数据节点/计算节点。代理节点和控制节点不可用。

## 返回值

布尔标量。

## 例子

```dolphindb
isDataNodeInitialized()
// output: true
```

相关函数：[isControllerInitialized](isControllerInitialized.html)
