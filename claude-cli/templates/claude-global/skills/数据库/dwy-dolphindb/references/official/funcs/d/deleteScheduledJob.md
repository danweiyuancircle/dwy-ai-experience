---
source_url: https://docs.dolphindb.cn/zh/funcs/d/deleteScheduledJob.html
fetched_at: 2026-05-19T09:18:41Z
category: funcs
title: deleteScheduledJob
sha1: 0fa3837333eb85cfa3d60d490f4469f829052f58
---

# deleteScheduledJob

## 语法

`deleteScheduledJob(jobId)`

## 详情

删除一个定时任务。如果指定的任务 ID 不存在，则抛出异常。

## 参数

**jobId** 是一个表示定时任务 ID 的字符串。

## 返回值

无。

## 例子

```dolphindb
deleteScheduledJob(`dailyJob1);
```
