---
source_url: https://docs.dolphindb.cn/zh/funcs/r/renameCatalogName.html
fetched_at: 2026-05-19T09:35:52Z
category: funcs
title: renameCatalogName
sha1: df2f1e73d81c4f5b5ae008d9d48e58b7dd2958cb
---

# renameCatalogName

首发版本：3.00.4

## 语法

`renameCatalogName(catalog, schema, oldName,
newName)`

## 详情

修改全限定名 `<catalog>.<schema>.<name>` 中的 name。

## 参数

**catalog** STRING 类型标量，表示 catalog 的名称。

**schema** STRING 类型标量，表示 schema 名称，可以是 orca\_graph, orca\_table 或 orca\_engine。

**oldName** STRING 类型标量，表示修改前的 name。

**newName** STRING 类型标量，表示修改后的 name。

## 例子

```dolphindb
renameCatalogName(catalog="demo1", schema="orca_graph", oldName="factor1", newName="factor2")

renameCatalogName(catalog="demo2", schema="orca_engine", oldName="engine1", newName="engine2")

renameCatalogName(catalog="demo3", schema="orca_table", oldName="trades1", newName="trades2")
```
