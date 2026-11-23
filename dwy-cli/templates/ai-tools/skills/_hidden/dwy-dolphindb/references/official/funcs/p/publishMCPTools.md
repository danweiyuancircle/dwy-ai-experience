---
source_url: https://docs.dolphindb.cn/zh/funcs/p/publishMCPTools.html
fetched_at: 2026-05-19T09:34:35Z
category: funcs
title: publishMCPTools
sha1: 013ff99320726d1460335fc9354c27732e346079
---

# publishMCPTools

首发版本：3.00.4

## 语法

`publishMCPTools([names])`

## 详情

发布 MCP tool 。

## 参数

**names** 可选参数，STRING 类型标量或向量，表示 tool 的名称。

## 返回值

STRING 类型向量，表示发布成功的 tool 名称。

## 例子

```dolphindb
publishMCPTools("myTool")
```
