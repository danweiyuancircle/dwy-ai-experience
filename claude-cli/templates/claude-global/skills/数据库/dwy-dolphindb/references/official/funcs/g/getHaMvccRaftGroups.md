---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getHaMvccRaftGroups.html
fetched_at: 2026-05-19T09:23:54Z
category: funcs
title: getHaMvccRaftGroups
sha1: 75e7c18ce3356902f7ae2834dc852b7144fea979
---

# getHaMvccRaftGroups

首发版本：3.00.5

## 语法

`getHaMvccRaftGroups()`

## 详情

获取当前节点所在的、与 MVCC 表高可用相关的 Raft 组信息。

## 返回值

返回一个表，包含以下列：

- id：INT 类型列，表示 MVCC Raft 组 ID。
- sites：STRING 类型列，展示该 Raft 组包含的节点信息。

## 例子

```dolphindb
getHaMvccRaftGroups()
```

| id | sites |
| --- | --- |
| 5 | dnode1,dnonde2,cnode1 |

**相关函数**：[haMvccTable](../h/haMvccTable.html)
