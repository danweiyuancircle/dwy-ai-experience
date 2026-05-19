---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropMCPPrompt.html
fetched_at: 2026-05-19T09:19:25Z
category: funcs
title: dropMCPPrompt
sha1: a4b9dee7e189d37e2b5758f5fc4fb8ddc2f4005c
---

# dropMCPPrompt

首发版本：3.00.4

## 语法

`dropMCPPrompt(name)`

## 详情

删除一个 MCP prompt 模板。如果该模板已被发布，需要先调用 `withdrawMCPPrompts` 撤销发布后才能删除。

## 参数

**name** STRING 类型标量，表示 prompt 模板的名称。

## 返回值

一个字符串，表示删除 MCP prompt 模板的名称。

## 例子

```dolphindb
dropMCPPrompt("stock_summary")
// output:'stock_summary'
```
