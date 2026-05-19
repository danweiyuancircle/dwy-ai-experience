---
source_url: https://docs.dolphindb.cn/zh/funcs/s/syntax.html
fetched_at: 2026-05-19T09:41:14Z
category: funcs
title: syntax
sha1: 2edba8b9ba2e56944d28af683425acfac90b1461
---

# syntax

## 语法

`syntax(X)`

## 详情

返回 *X* 表示的函数或命令的语法。

## 参数

**X** 是 DolphinDB 函数或命令。

## 返回值

STRING 类型标量。

## 例子

```dolphindb
syntax(createPartitionedTable);
// output
createPartitionedTable(dbHandle, table, tableName, [partitionColumns], [compressMethods])
```
