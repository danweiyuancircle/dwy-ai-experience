---
source_url: https://docs.dolphindb.cn/zh/funcs/s/startDataNode.html
fetched_at: 2026-05-19T09:39:58Z
category: funcs
title: startDataNode
sha1: dff80f17b2080c87f9c4bfb106250e39b4117d2c
---

# startDataNode

## 语法

`startDataNode(X)`

## 详情

用于在集群控制器上启动数据节点/计算节点。

## 参数

**X** 是一个向量。包含了要启动的数据节点/计算节点的信息。

## 例子

```dolphindb
x = ["192.168.1.27:8506","192.168.1.27:8502","192.168.1.27:8527"]
startDataNode(x);
```
