---
source_url: https://docs.dolphindb.cn/zh/funcs/s/stopDataNode.html
fetched_at: 2026-05-19T09:40:11Z
category: funcs
title: stopDataNode
sha1: 4d4f249d576a79eeef42be9e1b3bc8d51a1f09ac
---

# stopDataNode

## 语法

`stopDataNode(X)`

## 详情

用于在集群控制器上停止数据节点/计算节点。

## 参数

**X** 是一个向量。包含了要停止的数据节点/计算节点的信息。

## 例子

```dolphindb
x = ["192.168.1.27:8506","192.168.1.27:8502","192.168.1.27:8527"]
stopDataNode(x);
```
