---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getMemLimitOfQueryResult.html
fetched_at: 2026-05-19T09:24:59Z
category: funcs
title: getMemLimitOfQueryResult
sha1: 73a84636616ebdadbaf0bbc31936a8a0a73fa06a
---

# getMemLimitOfQueryResult

## 语法

`getMemLimitOfQueryResult()`

## 详情

获取单次查询结果占用的内存上限（单位为字节）。

## 参数

无

## 返回值

DOUBLE 类型标量。

## 例子

```dolphindb
setMemLimitOfQueryResult(0.2)
getMemLimitOfQueryResult() / 1024 / 1024 / 1024
// output: 0.2
```

相关函数：[setMemLimitOfQueryResult](../s/setMemLimitOfQueryResult.html)
