---
source_url: https://docs.dolphindb.cn/zh/funcs/a/addMCPPrompt.html
fetched_at: 2026-05-19T09:12:43Z
category: funcs
title: addMCPPrompt
sha1: 19603596e3056fa1c0519b66b09d21db957a51e4
---

# addMCPPrompt

首发版本：3.00.4

## 语法

`addMCPPrompt(name, message, [description], [extraInfo])`

## 详情

定义一个 MCP prompt 模板。

## 参数

**name** STRING 类型标量，表示 prompt 模板的名称。

**message** STRING 类型标量，表示 prompt 模板内容，允许包含 `{}`占位符。

**description** 可选参数，STRING 类型标量，表示 prompt 模板说明。

**extraInfo** 可选参数，一个字典，键是 STRING 类型，值是 ANY 或 STRING 类型，用于指定其他信息。目前键支持
"title"。

## 返回值

一个字符串，表示新增 MCP prompt 模板的名称。

## 例子

```dolphindb
addMCPPrompt(
  name = "stock_summary",
  message = "请用一句话总结 ${stock} 从 ${startDate} 到 ${endDate} 的走势。",
  description = "生成某个股票在一段时间内的自然语言概述",
  extraInfo = {title : "股票走势总结"}
)

//output:'stock_summary'
```
