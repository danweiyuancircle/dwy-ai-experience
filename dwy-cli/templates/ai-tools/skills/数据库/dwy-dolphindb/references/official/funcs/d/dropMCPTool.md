---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropMCPTool.html
fetched_at: 2026-05-19T09:19:27Z
category: funcs
title: dropMCPTool
sha1: 7240cce6f70517ca75d0b6c3f4c3dff6e9770bd8
---

# dropMCPTool

首发版本：3.00.4

## 语法

`dropMCPTool(name)`

## 详情

删除一个 MCP tool。如果该 tool 已被发布，需要先调用 `withdrawMCPTools` 撤销发布后才能删除。

## 参数

**name** STRING 类型标量，表示 tool 的名称。

## 返回值

一个字符串，表示删除 tool 的名称。

## 例子

```dolphindb
dropMCPTool("myTool")
```
