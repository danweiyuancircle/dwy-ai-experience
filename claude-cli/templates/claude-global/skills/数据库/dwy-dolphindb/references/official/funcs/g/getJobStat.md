---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getJobStat.html
fetched_at: 2026-05-19T09:24:46Z
category: funcs
title: getJobStat
sha1: 87025de792ee730cad02cac934915c6eefff8ab6
---

# getJobStat

## 语法

`getJobStat()`

## 详情

监控正在执行或者队列中的作业和任务的数量。

## 参数

无

## 返回值

返回一个字典，其 key 的含义为：

| 参数 | 含义 |
| --- | --- |
| queuedLocalTasks | 等待执行的本地任务数。 |
| runningLocalTasks | 正在执行的本地任务数。 |
| queuedJobs | 队列中的作业数。 |
| runningJobs | 正在执行的作业数。 |
| queuedRemoteTasks | 发送到远程执行的任务数。 |

## 例子

```dolphindb
getJobStat();
```

返回：

```dolphindb
queuedLocalTasks->0
runnningJobs->0
queuedRemoteTasks->0
queuedJobs->0
runningLocalTasks->0
```
