---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getRecoveryWorkerNum.html
fetched_at: 2026-05-19T09:25:40Z
category: funcs
title: getRecoveryWorkerNum
sha1: c41006a5188cb2fda9239521762ca6c2c2a29ffa
---

# getRecoveryWorkerNum

## 语法

`getRecoveryWorkerNum()`

## 详情

获取当前节点用于 chunk 恢复的工作线程数。

## 参数

无

## 返回值

整型标量。

## 例子

```dolphindb
resetRecoveryWorkerNum(2)
getRecoveryWorkerNum()
// output: 2
```

相关函数：[resetRecoveryWorkerNum](../r/resetRecoveryWorkerNum.html)
