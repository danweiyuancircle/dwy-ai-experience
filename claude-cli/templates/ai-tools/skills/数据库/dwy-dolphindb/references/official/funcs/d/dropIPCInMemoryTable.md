---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropIPCInMemoryTable.html
fetched_at: 2026-05-19T09:19:24Z
category: funcs
title: dropIPCInMemoryTable
sha1: 4841adb8ac716800fd6c32e2d2092d4745704768
---

# dropIPCInMemoryTable

## 语法

`dropIPCInMemoryTable(tableName)`

## 详情

删除跨进程共享内存表。

注：

- 此函数仅适用于 Linux 系统。
- server 关机并不能删除跨进程共享内存表，仍然需要通过 `dropIPCInMemoryTable`
  进行删除。

## 参数

**tableName** 字符串，表示跨进程共享内存表的名称。

## 返回值

一个字符串，表示删除的跨进程共享内存表的名称。

## 例子

删除函数 `createIPCInMemoryTable` 例子中创建的表 ipc\_table。

```dolphindb
dropIPCInMemoryTable(`ipc_table)
// output
ipc_table
```
