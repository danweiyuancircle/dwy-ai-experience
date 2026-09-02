---
source_url: https://docs.dolphindb.cn/zh/funcs/c/checkpointHaMvcc.html
fetched_at: 2026-05-19T09:15:01Z
category: funcs
title: checkpointHaMvcc
sha1: 8915f9a0eb1c83896a0cc16dfb5a58d8fbe06835
---

# checkpointHaMvcc

首发版本：3.00.5

## 语法

`checkpointHaMvcc(groupId)`

## 详情

手动触发指定 MVCC Raft 组的 checkpoint。

## 参数

**groupId** 是一个整数，表示 MVCC Raft 组 ID。

## 例子

```dolphindb
checkpointHaMvcc(5)
```

**相关函数**：[haMvccTable](../h/haMvccTable.html)
