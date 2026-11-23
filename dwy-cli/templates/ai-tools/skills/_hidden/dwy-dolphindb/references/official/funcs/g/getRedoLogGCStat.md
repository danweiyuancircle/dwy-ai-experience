---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getRedoLogGCStat.html
fetched_at: 2026-05-19T09:25:42Z
category: funcs
title: getRedoLogGCStat
sha1: 35463b32e87f43a6c5cf026deae2cade5a01dbda
---

# getRedoLogGCStat

## 语法

`getRedoLogGCStat()`

## 详情

获取 redo log 垃圾回收的状态。

## 参数

无

## 返回值

返回一个表对象，包含以下几列：

- physicalName：物理表名，格式为 "/数据库名/物理表名"
- txnCount：redo log 尚未回收的事务数
- numOfTxnPendingGC：等待回收的事务数
- minTidPendingGC：等待回收的事务的最小 tid
- numOfTxnPendingFlush：等待刷盘的事务数
- minTidPendingFlush：等待刷盘的事务的最小 tid

## 例子

```dolphindb
getRedoLogGCStat();
```

| physicalName | txnCount | numOfTxnPendingGC | minTidPendingGC | numOfTxnPendingFlush | minTidPendingFlush |
| --- | --- | --- | --- | --- | --- |
| /test/pt\_2 | 2 | 0 |  | 2 | 1031 |
| /listdb/pt\_2 | 1 | 1 | 1033 | 0 |  |
