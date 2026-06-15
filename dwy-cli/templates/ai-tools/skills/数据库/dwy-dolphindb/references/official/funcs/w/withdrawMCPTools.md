---
source_url: https://docs.dolphindb.cn/zh/funcs/w/withdrawMCPTools.html
fetched_at: 2026-05-19T09:44:03Z
category: funcs
title: withdrawMCPTools
sha1: f837ebe696669976127ddbe7ca2961cb182cadeb
---

# withdrawMCPTools

首发版本：3.00.4

## 语法

`withdrawMCPTools([names])`

## 详情

撤销已发布的 MCP tool。

## 参数

**names** 可选参数，STRING 类型标量或向量，表示 tool 的名称。

## 返回值

一个 STRING 类型向量，表示撤销成功的 tool。

## 例子

```dolphindb
withdrawMCPTools("myTool")
```
