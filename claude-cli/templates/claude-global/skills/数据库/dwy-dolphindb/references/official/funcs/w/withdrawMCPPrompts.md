---
source_url: https://docs.dolphindb.cn/zh/funcs/w/withdrawMCPPrompts.html
fetched_at: 2026-05-19T09:44:01Z
category: funcs
title: withdrawMCPPrompts
sha1: d30f58e55ba9eab5548ca9a01f55789e5c9aa879
---

# withdrawMCPPrompts

首发版本：3.00.4

## 语法

`withdrawMCPPrompts([names])`

## 详情

撤销已发布的 MCP prompt 模板。

## 参数

**names** 可选参数，STRING 类型标量或向量，表示 prompt 模板的名称。

## 返回值

一个 STRING 类型向量，表示撤销成功的 prompt 模板。

## 例子

```dolphindb
withdrawMCPPrompts("stock_summary")
// output:["stock_summary"]
```
