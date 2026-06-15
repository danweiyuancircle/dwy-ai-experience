---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropHaMvccTable.html
fetched_at: 2026-05-19T09:19:23Z
category: funcs
title: dropHaMvccTable
sha1: 56991dff9dac3bea55af18d80a0aa19c9b05b848
---

# dropHaMvccTable

首发版本：3.00.5

## 语法

`dropHaMvccTable(tableName)`

## 详情

删除指定名称的高可用 MVCC 表。

此函数必须在该表所属 Raft 组的 Leader 节点上执行。

## 参数

**tableName** 字符串标量，表示要删除的高可用 MVCC 表的名称。

## 例子

```dolphindb
dropHaMvccTable("demoHaMvcc")
```

**相关函数**：[haMvccTable](../h/haMvccTable.html), [loadHaMvccTable](../l/loadHaMvccTable.html)
