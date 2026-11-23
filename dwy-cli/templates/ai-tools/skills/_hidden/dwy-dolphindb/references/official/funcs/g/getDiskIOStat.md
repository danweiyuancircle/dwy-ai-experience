---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getDiskIOStat.html
fetched_at: 2026-05-19T09:23:39Z
category: funcs
title: getDiskIOStat
sha1: beaa9d70ded224affd90181336da93c775d701b7
---

# getDiskIOStat

## 语法

`getDiskIOStat()`

## 详情

获取磁盘 I/O 统计信息。

## 参数

无

## 返回值

返回包含两个键值对的字典：

- diskIOQueueDepths 是一个向量，表示每个 IO 队列的深度。在同一个 DolphinDB
  实例中的所有 IO 任务都属于同一个 IO 队列。
- diskIOConcurrencyLevel 是一个整数，表示 IO 队列的数量。

## 例子

```dolphindb
getDiskIOStat()

// output
diskIOQueueDepths->[0]
diskIOConcurrnecyLevel->1
```
