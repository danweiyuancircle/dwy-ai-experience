---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getHaMvccLeader.html
fetched_at: 2026-05-19T09:23:53Z
category: funcs
title: getHaMvccLeader
sha1: beac56d26b42e75d3c936acf9d0fc18c072a2f57
---

# getHaMvccLeader

首发版本：3.00.5

## 语法

`getHaMvccLeader(groupId)`

## 详情

获取指定 MVCC Raft 组的 Leader 节点别名。

## 参数

**groupId** 是一个整数，表示 MVCC Raft 组 ID。

## 返回值

STRING 类型标量。

## 例子

```dolphindb
getHaMvccLeader(5)
// output
"dnode1"
```

**相关函数**：[haMvccTable](../h/haMvccTable.html)
