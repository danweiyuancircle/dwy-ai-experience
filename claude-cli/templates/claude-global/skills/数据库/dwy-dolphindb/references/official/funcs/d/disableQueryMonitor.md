---
source_url: https://docs.dolphindb.cn/zh/funcs/d/disableQueryMonitor.html
fetched_at: 2026-05-19T09:19:02Z
category: funcs
title: disableQueryMonitor
sha1: 3b2a4b4e1b05835adc519840fce49adda6ddf079
---

# disableQueryMonitor

## 语法

`disableQueryMonitor()`

## 详情

关闭监控查询任务状态的功能。

由于监控查询任务状态具有一定的内存开销，内存资源紧张时，可以关闭该功能。注意：调用该命令后，用户将无法调用 [getQueryStatus](../g/getQueryStatus.html) 函数获取查询任务的状态。

## 参数

无。

## 返回值

无。

相关函数： [enableQueryMonitor](../e/enableQueryMonitor.html)
