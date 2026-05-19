---
source_url: https://docs.dolphindb.cn/zh/funcs/i/isCheckpointingHaMvcc.html
fetched_at: 2026-05-19T09:28:19Z
category: funcs
title: isCheckpointingHaMvcc
sha1: d81f0aeb38940e20e69c4ada1b6699a5c43378d6
---

# isCheckpointingHaMvcc

首发版本：3.00.5

## 语法

`isCheckpointingHaMvcc(groupId)`

## 详情

检查指定 MVCC Raft 组当前是否正在执行 checkpoint。

## 参数

**groupId** 是一个整数，表示 MVCC Raft 组 ID。

## 返回值

BOOL 类型标量。

## 例子

```dolphindb
isCheckpointingHaMvcc(5)
// output:false
```

**相关函数**：[haMvccTable](../h/haMvccTable.html)
