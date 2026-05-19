---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getDfsRecoveryConcurrency.html
fetched_at: 2026-05-19T09:23:37Z
category: funcs
title: getDfsRecoveryConcurrency
sha1: 43bef15437fd536864a11d678c3714ea07ce3ab0
---

# getDfsRecoveryConcurrency

## 语法

`getDfsRecoveryConcurrency()`

## 详情

获取控制节点上允许的分区恢复任务的最大并发数。此函数只能由管理员在控制节点调用。

## 参数

无

## 返回值

整型标量。

## 例子

```dolphindb
getDfsRecoveryConcurrency()
```

相关函数：[resetDfsRecoveryConcurrency](../r/resetDfsRecoveryConcurrency.html)
