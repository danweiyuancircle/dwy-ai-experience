---
source_url: https://docs.dolphindb.cn/zh/funcs/l/loadIPCInMemoryTable.html
fetched_at: 2026-05-19T09:29:56Z
category: funcs
title: loadIPCInMemoryTable
sha1: 1d546848b4859d99703d13610fa2bfbf897640fe
---

# loadIPCInMemoryTable

## 语法

`loadIPCInMemoryTable(tableName)`

## 详情

加载跨进程共享内存表，并返回该表的句柄。

注意：此函数仅适用于 Linux 系统。

## 参数

**tableName** 字符串，表示跨进程共享内存表的名称。

## 返回值

一个共享内存表句柄。

## 例子

加载函数 `createIPCInMemoryTable` 例子中创建的表 ipc\_table。

```dolphindb
ipc_t = loadIPCInMemoryTable("ipc_table")
ipc_t
// output
timestamp temperature
```
