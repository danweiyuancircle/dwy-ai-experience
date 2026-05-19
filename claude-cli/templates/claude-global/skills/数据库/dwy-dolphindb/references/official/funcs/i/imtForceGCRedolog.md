---
source_url: https://docs.dolphindb.cn/zh/funcs/i/imtForceGCRedolog.html
fetched_at: 2026-05-19T09:27:38Z
category: funcs
title: imtForceGCRedolog
sha1: 65403fc5a8d713995ba80e59aa65bbce1c26a08e
---

# imtForceGCRedolog

## 语法

`imtForceGCRedolog(tid)`

## 详情

系统会自动将已完成（处于 COMPLETE 状态）事务的 redo log 将放入待回收列表。并根据此列表中事务 tid
的大小，顺序对成功落盘的事务进行回收。

若回收过程中出现某个编号为 tid 的事务尚未刷盘，在该事务被成功刷盘前，无法对编号大于 *tid* 且成功刷盘事务的
redo log 进行回收。此时调用该命令，可以取消等待编号为 *tid* 事务的回收，继续对后续满足回收条件的事务进行回收。

该函数建议搭配 [getRedoLogGCStat](../g/getRedoLogGCStat.html) 函数使用。

## 参数

**tid** 事务的 id。

## 返回值

无。
