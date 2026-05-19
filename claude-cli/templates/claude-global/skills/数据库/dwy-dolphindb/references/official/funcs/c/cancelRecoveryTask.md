---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cancelRecoveryTask.html
fetched_at: 2026-05-19T09:14:32Z
category: funcs
title: cancelRecoveryTask
sha1: 89b5917573e2f6b96cee8a4875eb3a824a4d9026
---

# cancelRecoveryTask

## 语法

`cancelRecoveryTask(taskId)`

## 详情

取消已经提交但尚未开始执行的副本恢复任务。该命令只能由管理员在控制节点上执行。

## 参数

**taskId** 是一个字符串标量或向量，表示副本恢复任务的 ID，可以通过 [getRecoveryTaskStatus](../g/getRecoveryTaskStatus.html) 获得。

## 返回值

无。
