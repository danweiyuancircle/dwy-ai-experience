---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getSystemCpuUsage.html
fetched_at: 2026-05-19T09:26:18Z
category: funcs
title: getSystemCpuUsage
sha1: d61ccbbf291b6f27f40d20efea6e4f5555b28749
---

# getSystemCpuUsage

## 语法

`getSystemCpuUsage()`

## 详情

返回当前节点上 DolphinDB 进程实时占用 CPU 的百分比。

注意，若 DolphinDB 进程占用多个 CPU，则返回各个 CPU 占用率的总和。

## 参数

无

## 返回值

DOUBLE 标量。

## 例子

```dolphindb
getSystemCpuUsage();

// output: 1.771654
```
