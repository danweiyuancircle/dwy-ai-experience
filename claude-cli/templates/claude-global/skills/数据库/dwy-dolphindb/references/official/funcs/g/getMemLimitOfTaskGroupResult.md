---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getMemLimitOfTaskGroupResult.html
fetched_at: 2026-05-19T09:25:00Z
category: funcs
title: getMemLimitOfTaskGroupResult
sha1: 97ed6509d42568dea4e1c9ccded3de6fe524ee15
---

# getMemLimitOfTaskGroupResult

## 语法

`getMemLimitOfTaskGroupResult()`

## 详情

获取当前节点发送的批量子查询占用的内存上限（单位为字节）。

## 参数

无

## 返回值

DOUBLE 类型标量。

## 例子

```dolphindb
setMemLimitOfTaskGroupResult(10)
getMemLimitOfTaskGroupResult() / 1024 / 1024 / 1024
// output: 10
```

相关函数：[setMemLimitOfTaskGroupResult](../s/setMemLimitOfTaskGroupResult.html)
