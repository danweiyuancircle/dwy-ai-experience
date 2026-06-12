---
source_url: https://docs.dolphindb.cn/zh/funcs/p/publishMCPPrompts.html
fetched_at: 2026-05-19T09:34:34Z
category: funcs
title: publishMCPPrompts
sha1: 01980a17c9639e80e2f7ede7d633b7fda4b1a9a6
---

# publishMCPPrompts

首发版本：3.00.4

## 语法

`publishMCPPrompts([names])`

## 详情

发布 MCP prompt 模板。

## 参数

**names** 可选参数，STRING 类型标量或向量，表示 prompt 模板的名称。

## 返回值

STRING 类型向量，表示发布成功的 prompt 模板名称。

## 例子

```dolphindb
publishMCPPrompts("stock_summary")
// output:["stock_summary"]
```
