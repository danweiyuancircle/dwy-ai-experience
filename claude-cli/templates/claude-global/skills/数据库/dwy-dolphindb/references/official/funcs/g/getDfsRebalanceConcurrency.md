---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getDfsRebalanceConcurrency.html
fetched_at: 2026-05-19T09:23:35Z
category: funcs
title: getDfsRebalanceConcurrency
sha1: 3892aacdc3cfe280af26425d18747782d9973d2a
---

# getDfsRebalanceConcurrency

## 语法

`getDfsRebalanceConcurrency()`

## 详情

获取控制节点上允许的再平衡任务的最大并发数。此函数只能由管理员在控制节点调用。

## 参数

无

## 返回值

整型标量。

## 例子

```dolphindb
getDfsRebalanceConcurrency()
```

相关函数：[resetDfsRebalanceConcurrency](../r/resetDfsRebalanceConcurrency.html)
