---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cancelpkeycompactiontask.html
fetched_at: 2026-05-19T09:14:30Z
category: funcs
title: cancelPKEYCompactionTask
sha1: 6882f3cf27b94e6c118795d202f83857b55e53f1
---

# cancelPKEYCompactionTask

## 语法

`cancelPKEYCompactionTask(chunkId)`

## 详情

取消目标分区正在执行的 compaction 任务。

## 参数

**chunkId** STRING 类型标量，表示 chunk 对应的 ID。

## 返回值

无。

## 例子

```dolphindb
triggerPKEYCompaction(chunkId="1486f935-6f87-479c-b341-34c6a303d4f9", async=false)
```
